import datetime
import json
import luigi
from os import path

import common
import extract_batch
import load_lang


class LoadProfession(luigi.Task):
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
            "load_profession",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.json".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        return extract_batch.ExtractBatch(
            entity_schema="../schema/gw2/v2/professions/profession.json",
            extract_datetime=self.extract_datetime,
            extract_dir=path.join(self.output_dir, "extract_profession_id"),
            id_schema="../schema/gw2/v2/professions/index.json",
            output_file=path.join(
                self.output_dir,
                "extract_profession",
                target_filename,
            ),
            url_params={"lang": self.lang_tag.value, "v": "2019-12-19T00:00:00.000Z"},
            url="https://api.guildwars2.com/v2/professions",
        )

    def run(self):
        with self.input().open("r") as ro_input_file:
            json_input = json.load(fp=ro_input_file)

        with (
            common.get_conn() as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute(query="BEGIN")
            try:
                for profession in json_input:
                    profession_id = profession["id"]
                    cursor.execute(
                        **upsert_profession(
                            code=profession["code"],
                            icon_big=profession["icon_big"],
                            icon=profession["icon"],
                            profession_id=profession_id,
                        )
                    )

                    profession_name = profession["name"]
                    cursor.execute(
                        **load_lang.upsert_operating_copy(
                            app_name="gw2",
                            lang_tag=self.lang_tag.value,
                            original=profession_name,
                        )
                    )
                    cursor.execute(
                        **upsert_profession_name(
                            app_name="gw2",
                            lang_tag=self.lang_tag.value,
                            original=profession_name,
                            profession_id=profession_id,
                        )
                    )

                cursor.execute(query="COMMIT")
                connection.commit()
                with self.output().open("w") as w_output:
                    w_output.write("ok")

            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                raise exception_instance


def upsert_profession(
    code: int, icon_big: str, icon: str, profession_id: str
) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.profession AS target_profession
USING (
  VALUES (%(code)s::integer,
    %(icon_big)s::text,
    %(icon)s::text,
    %(profession_id)s::text)
) AS source_profession (code, icon_big, icon, profession_id)
ON
  target_profession.profession_id = source_profession.profession_id
WHEN MATCHED
  AND target_profession.code != source_profession.code 
  OR target_profession.icon_big != source_profession.icon_big
  OR target_profession.icon != source_profession.icon THEN
  UPDATE SET
    (code, icon_big, icon) = (source_profession.code,
      source_profession.icon_big,
      source_profession.icon)
WHEN NOT MATCHED THEN
  INSERT (code, icon_big, icon, profession_id)
    VALUES (source_profession.code,
      source_profession.icon_big,
      source_profession.icon,
      source_profession.profession_id);
""",
        "params": {
            "code": code,
            "icon_big": icon_big,
            "icon": icon,
            "profession_id": profession_id,
        },
    }


def upsert_profession_name(
    app_name: str, lang_tag: str, original: str, profession_id: int
):
    return {
        "query": """
MERGE INTO gwapese.profession_name AS target_profession_name
USING (
  VALUES (%(app_name)s::text,
    %(lang_tag)s::text,
    %(original)s::text,
    %(profession_id)s::text)
) AS source_profession_name (app_name, lang_tag, original, profession_id)
  ON target_profession_name.app_name = source_profession_name.app_name
  AND target_profession_name.lang_tag = source_profession_name.lang_tag
  AND target_profession_name.profession_id = source_profession_name.profession_id
WHEN MATCHED
  AND target_profession_name.original != source_profession_name.original THEN
  UPDATE SET
    original = source_profession_name.original
WHEN NOT MATCHED THEN
  INSERT (app_name, lang_tag, original, profession_id)
    VALUES (source_profession_name.app_name,
      source_profession_name.lang_tag,
      source_profession_name.original,
      source_profession_name.profession_id);""",
        "params": {
            "app_name": app_name,
            "lang_tag": lang_tag,
            "original": original,
            "profession_id": profession_id,
        },
    }
