import datetime
import json
import luigi
from os import path

import common
import extract_batch
import load_lang


class LoadNovelty(luigi.Task):
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
            "load_novelty",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.json".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        return extract_batch.ExtractBatch(
            entity_schema="../schema/gw2/v2/novelties/novelty.json",
            extract_datetime=self.extract_datetime,
            extract_dir=path.join(self.output_dir, "extract_novelty_id"),
            id_schema="../schema/gw2/v2/novelties/index.json",
            output_file=path.join(
                self.output_dir,
                "extract_novelty",
                target_filename,
            ),
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/novelties",
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
                for novelty in json_input:
                    novelty_id = novelty["id"]
                    cursor.execute(
                        **upsert_novelty(
                            icon=novelty["icon"],
                            novelty_id=novelty_id,
                            slot=novelty["slot"],
                        )
                    )

                    novelty_description = novelty["description"]
                    if novelty_description != "":
                        cursor.execute(
                            **load_lang.upsert_operating_copy(
                                app_name="gw2",
                                lang_tag=self.lang_tag.value,
                                original=novelty_description,
                            )
                        )
                        cursor.execute(
                            **upsert_novelty_description(
                                app_name="gw2",
                                novelty_id=novelty_id,
                                lang_tag=self.lang_tag.value,
                                original=novelty_description,
                            )
                        )

                    novelty_name = novelty["name"]
                    cursor.execute(
                        **load_lang.upsert_operating_copy(
                            app_name="gw2",
                            lang_tag=self.lang_tag.value,
                            original=novelty_name,
                        )
                    )
                    cursor.execute(
                        **upsert_novelty_name(
                            app_name="gw2",
                            novelty_id=novelty_id,
                            lang_tag=self.lang_tag.value,
                            original=novelty_name,
                        )
                    )

                cursor.execute(query="COMMIT")
                connection.commit()
                with self.output().open("w") as w_output:
                    w_output.write("ok")

            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                raise exception_instance


def upsert_novelty(icon: str, novelty_id: int, slot: str) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.novelty AS target_novelty
USING (
  VALUES (%(icon)s::text, %(novelty_id)s::integer, %(slot)s::text)
) AS source_novelty (icon, novelty_id, slot)
ON
  target_novelty.novelty_id = source_novelty.novelty_id
WHEN MATCHED
  AND target_novelty.icon != source_novelty.icon
  OR target_novelty.slot != source_novelty.slot THEN
  UPDATE SET
    (icon, slot) =
      (source_novelty.icon, source_novelty.slot)
WHEN NOT MATCHED THEN
  INSERT (icon, novelty_id, slot)
    VALUES (source_novelty.icon,
      source_novelty.novelty_id,
      source_novelty.slot);
""",
        "params": {"icon": icon, "novelty_id": novelty_id, "slot": slot},
    }


def upsert_novelty_description(
    app_name: str, lang_tag: str, novelty_id: int, original: str
):
    return {
        "query": """
MERGE INTO gwapese.novelty_description AS target_novelty_description
USING (
  VALUES (
    %(app_name)s::text, %(lang_tag)s::text, %(novelty_id)s::integer, %(original)s::text)
) AS
  source_novelty_description (app_name, lang_tag, novelty_id, original)
  ON target_novelty_description.app_name = source_novelty_description.app_name
  AND target_novelty_description.lang_tag = source_novelty_description.lang_tag
  AND target_novelty_description.novelty_id = source_novelty_description.novelty_id
WHEN MATCHED
  AND target_novelty_description.original != source_novelty_description.original THEN
  UPDATE SET
    original = source_novelty_description.original
WHEN NOT MATCHED THEN
  INSERT (app_name, lang_tag, novelty_id, original)
    VALUES (source_novelty_description.app_name,
      source_novelty_description.lang_tag,
      source_novelty_description.novelty_id,
      source_novelty_description.original);""",
        "params": {
            "app_name": app_name,
            "lang_tag": lang_tag,
            "novelty_id": novelty_id,
            "original": original,
        },
    }


def upsert_novelty_name(app_name: str, lang_tag: str, novelty_id: int, original: str):
    return {
        "query": """
MERGE INTO gwapese.novelty_name AS target_novelty_name
USING (
VALUES (%(app_name)s::text, %(lang_tag)s::text, %(novelty_id)s::integer, %(original)s::text)) AS
  source_novelty_name (app_name, lang_tag, novelty_id, original)
  ON target_novelty_name.app_name = source_novelty_name.app_name
  AND target_novelty_name.lang_tag = source_novelty_name.lang_tag
  AND target_novelty_name.novelty_id = source_novelty_name.novelty_id
WHEN MATCHED
  AND target_novelty_name.original != source_novelty_name.original THEN
  UPDATE SET
    original = source_novelty_name.original
WHEN NOT MATCHED THEN
  INSERT (app_name, lang_tag, novelty_id, original)
    VALUES (source_novelty_name.app_name,
      source_novelty_name.lang_tag,
      source_novelty_name.novelty_id,
      source_novelty_name.original);""",
        "params": {
            "app_name": app_name,
            "lang_tag": lang_tag,
            "novelty_id": novelty_id,
            "original": original,
        },
    }
