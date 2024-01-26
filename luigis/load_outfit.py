import datetime
import json
import luigi
from os import path

import common
import extract_batch
import load_lang


class LoadOutfit(luigi.Task):
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
            "load_outfit",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.json".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        return extract_batch.ExtractBatch(
            entity_schema="../schema/gw2/v2/outfits/outfit.json",
            extract_datetime=self.extract_datetime,
            extract_dir=path.join(self.output_dir, "extract_outfit_id"),
            id_schema="../schema/gw2/v2/outfits/index.json",
            output_file=path.join(
                self.output_dir,
                "extract_outfit",
                target_filename,
            ),
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/outfits",
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
                for outfit in json_input:
                    outfit_id = outfit["id"]
                    cursor.execute(
                        **upsert_outfit(icon=outfit["icon"], outfit_id=outfit_id)
                    )

                    outfit_name = outfit["name"]
                    cursor.execute(
                        **load_lang.upsert_operating_copy(
                            app_name="gw2",
                            lang_tag=self.lang_tag.value,
                            original=outfit_name,
                        )
                    )
                    cursor.execute(
                        **upsert_outfit_name(
                            app_name="gw2",
                            outfit_id=outfit_id,
                            lang_tag=self.lang_tag.value,
                            original=outfit_name,
                        )
                    )

                cursor.execute(query="COMMIT")
                connection.commit()
                with self.output().open("w") as w_output:
                    w_output.write("ok")

            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                raise exception_instance


def upsert_outfit(icon: str, outfit_id: int) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.outfit AS target_outfit
USING (
  VALUES (%(icon)s::text, %(outfit_id)s::integer)
) AS source_outfit (icon, outfit_id)
ON
  target_outfit.outfit_id = source_outfit.outfit_id
WHEN MATCHED
  AND target_outfit.icon != source_outfit.icon THEN
  UPDATE SET
    icon = source_outfit.icon
WHEN NOT MATCHED THEN
  INSERT (icon, outfit_id)
    VALUES (source_outfit.icon,
      source_outfit.outfit_id);
""",
        "params": {"icon": icon, "outfit_id": outfit_id},
    }


def upsert_outfit_name(app_name: str, lang_tag: str, outfit_id: int, original: str):
    return {
        "query": """
MERGE INTO gwapese.outfit_name AS target_outfit_name
USING (
VALUES (%(app_name)s::text, %(lang_tag)s::text, %(outfit_id)s::integer, %(original)s::text)) AS
  source_outfit_name (app_name, lang_tag, outfit_id, original)
  ON target_outfit_name.app_name = source_outfit_name.app_name
  AND target_outfit_name.lang_tag = source_outfit_name.lang_tag
  AND target_outfit_name.outfit_id = source_outfit_name.outfit_id
WHEN MATCHED
  AND target_outfit_name.original != source_outfit_name.original THEN
  UPDATE SET
    original = source_outfit_name.original
WHEN NOT MATCHED THEN
  INSERT (app_name, lang_tag, outfit_id, original)
    VALUES (source_outfit_name.app_name,
      source_outfit_name.lang_tag,
      source_outfit_name.outfit_id,
      source_outfit_name.original);""",
        "params": {
            "app_name": app_name,
            "lang_tag": lang_tag,
            "outfit_id": outfit_id,
            "original": original,
        },
    }
