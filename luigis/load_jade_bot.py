import datetime
import json
import luigi
from os import path

import common
import extract_batch
import load_lang


class LoadJadeBot(luigi.Task):
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
            "load_jade_bot",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.json".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        return extract_batch.ExtractBatch(
            entity_schema="../schema/gw2/v2/jadebots/jadebot.json",
            extract_datetime=self.extract_datetime,
            extract_dir=path.join(self.output_dir, "extract_jade_bot_id"),
            id_schema="../schema/gw2/v2/jadebots/index.json",
            output_file=path.join(
                self.output_dir,
                "extract_jade_bot",
                target_filename,
            ),
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/jadebots",
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
                for jade_bot in json_input:
                    jade_bot_id = jade_bot["id"]
                    cursor.execute(**upsert_jade_bot(jade_bot_id=jade_bot_id))

                    jade_bot_description = jade_bot["description"]
                    cursor.execute(
                        **load_lang.upsert_operating_copy(
                            app_name="gw2",
                            lang_tag=self.lang_tag.value,
                            original=jade_bot_description,
                        )
                    )
                    cursor.execute(
                        **upsert_jade_bot_description(
                            app_name="gw2",
                            jade_bot_id=jade_bot_id,
                            lang_tag=self.lang_tag.value,
                            original=jade_bot_description,
                        )
                    )

                    jade_bot_name = jade_bot["name"]
                    cursor.execute(
                        **load_lang.upsert_operating_copy(
                            app_name="gw2",
                            lang_tag=self.lang_tag.value,
                            original=jade_bot_name,
                        )
                    )
                    cursor.execute(
                        **upsert_jade_bot_name(
                            app_name="gw2",
                            jade_bot_id=jade_bot_id,
                            lang_tag=self.lang_tag.value,
                            original=jade_bot_name,
                        )
                    )

                cursor.execute(query="COMMIT")
                connection.commit()

                with self.output().open("w") as w_output:
                    w_output.write("ok")

            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                raise exception_instance


def upsert_jade_bot(jade_bot_id: int) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.jade_bot AS target_jade_bot
USING (
  VALUES (%(jade_bot_id)s::integer)
) AS source_jade_bot (jade_bot_id)
ON
  target_jade_bot.jade_bot_id = source_jade_bot.jade_bot_id
WHEN NOT MATCHED THEN
  INSERT (jade_bot_id)
    VALUES (source_jade_bot.jade_bot_id);
""",
        "params": {"jade_bot_id": jade_bot_id},
    }


def upsert_jade_bot_description(
    app_name: str, jade_bot_id: int, lang_tag: str, original: str
):
    return {
        "query": """
MERGE INTO gwapese.jade_bot_description AS target_jade_bot_description
USING (
VALUES (%(app_name)s::text, %(jade_bot_id)s::integer,
  %(lang_tag)s::text, %(original)s::text)
) AS
  source_jade_bot_description (app_name, jade_bot_id, lang_tag, original)
  ON target_jade_bot_description.app_name = source_jade_bot_description.app_name
  AND target_jade_bot_description.lang_tag = source_jade_bot_description.lang_tag
  AND target_jade_bot_description.jade_bot_id = source_jade_bot_description.jade_bot_id
WHEN MATCHED
  AND target_jade_bot_description.original != source_jade_bot_description.original THEN
  UPDATE SET
    original = source_jade_bot_description.original
WHEN NOT MATCHED THEN
  INSERT (app_name, jade_bot_id, lang_tag, original)
    VALUES (source_jade_bot_description.app_name,
      source_jade_bot_description.jade_bot_id,
      source_jade_bot_description.lang_tag,
      source_jade_bot_description.original);""",
        "params": {
            "app_name": app_name,
            "jade_bot_id": jade_bot_id,
            "lang_tag": lang_tag,
            "original": original,
        },
    }


def upsert_jade_bot_name(app_name: str, jade_bot_id: int, lang_tag: str, original: str):
    return {
        "query": """
MERGE INTO gwapese.jade_bot_name AS target_jade_bot_name
USING (
VALUES (%(app_name)s::text, %(jade_bot_id)s::integer, %(lang_tag)s::text, %(original)s::text)) AS
  source_jade_bot_name (app_name, jade_bot_id, lang_tag, original)
  ON target_jade_bot_name.app_name = source_jade_bot_name.app_name
  AND target_jade_bot_name.lang_tag = source_jade_bot_name.lang_tag
  AND target_jade_bot_name.jade_bot_id = source_jade_bot_name.jade_bot_id
WHEN MATCHED
  AND target_jade_bot_name.original != source_jade_bot_name.original THEN
  UPDATE SET
    original = source_jade_bot_name.original
WHEN NOT MATCHED THEN
  INSERT (app_name, jade_bot_id, lang_tag, original)
    VALUES (source_jade_bot_name.app_name,
      source_jade_bot_name.jade_bot_id,
      source_jade_bot_name.lang_tag,
      source_jade_bot_name.original);""",
        "params": {
            "app_name": app_name,
            "jade_bot_id": jade_bot_id,
            "lang_tag": lang_tag,
            "original": original,
        },
    }
