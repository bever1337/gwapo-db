import datetime
import json
import luigi
from os import path

import common
import extract_batch
import load_lang


class LoadSpecialization(luigi.Task):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)

    def output(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.txt".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        target_path = path.join(
            self.output_dir,
            "load_specialization",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.ndjson".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        return extract_batch.ExtractBatch(
            entity_schema="../schema/gw2/v2/specializations/specialization.json",
            extract_datetime=self.extract_datetime,
            extract_dir=path.join(self.output_dir, "extract_specialization_id"),
            id_schema="../schema/gw2/v2/specializations/index.json",
            output_file=path.join(
                self.output_dir, "extract_specialization", target_filename
            ),
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/specializations",
        )

    def run(self):
        with (
            self.input().open("r") as ro_input_file,
            common.get_conn() as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute(query="BEGIN")
            try:
                for specialization_line in ro_input_file:
                    specialization = json.loads(specialization_line)
                    specialization_id = specialization["id"]
                    cursor.execute(
                        **upsert_specialization(
                            background=specialization["background"],
                            elite=specialization["elite"],
                            icon=specialization["icon"],
                            profession_id=specialization["profession"],
                            specialization_id=specialization_id,
                        )
                    )

                    specialization_name = specialization["name"]
                    cursor.execute(
                        **load_lang.upsert_operating_copy(
                            app_name="gw2",
                            lang_tag=self.lang_tag.value,
                            original=specialization_name,
                        )
                    )
                    cursor.execute(
                        **upsert_specialization_name(
                            app_name="gw2",
                            lang_tag=self.lang_tag.value,
                            original=specialization_name,
                            specialization_id=specialization_id,
                        )
                    )

                cursor.execute(query="COMMIT")
                connection.commit()
                with self.output().open("w") as w_output:
                    w_output.write("ok")

            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                raise exception_instance


def upsert_specialization(
    background: str, elite: bool, icon: str, profession_id: str, specialization_id: int
) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.specialization AS target_specialization
USING (
  VALUES (%(background)s::text,
    %(elite)s::boolean,
    %(icon)s::text,
    %(profession_id)s::text,
    %(specialization_id)s::integer)
) AS source_specialization (background, elite, icon, profession_id, specialization_id)
ON target_specialization.profession_id = source_specialization.profession_id
  AND target_specialization.specialization_id = source_specialization.specialization_id
WHEN MATCHED
  AND target_specialization.background != source_specialization.background
  OR target_specialization.elite != source_specialization.elite
  OR target_specialization.icon != source_specialization.icon THEN
  UPDATE SET
    (background, elite, icon) = (source_specialization.background,
      source_specialization.elite,
      source_specialization.icon)
WHEN NOT MATCHED THEN
  INSERT (background, elite, icon, profession_id, specialization_id)
    VALUES (source_specialization.background,
      source_specialization.elite,
      source_specialization.icon,
      source_specialization.profession_id,
      source_specialization.specialization_id);
""",
        "params": {
            "background": background,
            "elite": elite,
            "icon": icon,
            "profession_id": profession_id,
            "specialization_id": specialization_id,
        },
    }


def upsert_specialization_name(
    app_name: str, lang_tag: str, original: str, specialization_id: int
):
    return {
        "query": """
MERGE INTO gwapese.specialization_name AS target_specialization_name
USING (
  VALUES (%(app_name)s::text,
    %(lang_tag)s::text,
    %(original)s::text,
    %(specialization_id)s::integer)
) AS source_specialization_name (app_name, lang_tag, original, specialization_id)
  ON target_specialization_name.app_name = source_specialization_name.app_name
  AND target_specialization_name.lang_tag = source_specialization_name.lang_tag
  AND target_specialization_name.specialization_id = source_specialization_name.specialization_id
WHEN MATCHED
  AND target_specialization_name.original != source_specialization_name.original THEN
  UPDATE SET
    original = source_specialization_name.original
WHEN NOT MATCHED THEN
  INSERT (app_name, lang_tag, original, specialization_id)
    VALUES (source_specialization_name.app_name,
      source_specialization_name.lang_tag,
      source_specialization_name.original,
      source_specialization_name.specialization_id);""",
        "params": {
            "app_name": app_name,
            "lang_tag": lang_tag,
            "original": original,
            "specialization_id": specialization_id,
        },
    }
