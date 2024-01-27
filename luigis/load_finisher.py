import datetime
import json
import luigi
from os import path

import common
import extract_batch
import load_lang


class LoadFinisher(luigi.Task):
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
            "load_finisher",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.ndjson".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        return extract_batch.ExtractBatch(
            entity_schema="../schema/gw2/v2/finishers/finisher.json",
            extract_datetime=self.extract_datetime,
            extract_dir=path.join(self.output_dir, "extract_finisher_id"),
            id_schema="../schema/gw2/v2/finishers/index.json",
            output_file=path.join(
                self.output_dir,
                "extract_finisher",
                target_filename,
            ),
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/finishers",
        )

    def run(self):
        with (
            self.input().open("r") as ro_input_file,
            common.get_conn() as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute(query="BEGIN")
            try:
                for finisher_line in ro_input_file:
                    finisher = json.loads(finisher_line)
                    finisher_id = finisher["id"]
                    cursor.execute(
                        **upsert_finisher(
                            finisher_id=finisher_id,
                            icon=finisher["icon"],
                            presentation_order=finisher["order"],
                        )
                    )

                    finisher_detail = finisher["unlock_details"]
                    if finisher_detail != "":
                        cursor.execute(
                            **load_lang.upsert_operating_copy(
                                app_name="gw2",
                                lang_tag=self.lang_tag.value,
                                original=finisher_detail,
                            )
                        )
                        cursor.execute(
                            **upsert_finisher_detail(
                                app_name="gw2",
                                finisher_id=finisher_id,
                                lang_tag=self.lang_tag.value,
                                original=finisher_detail,
                            )
                        )

                    finisher_name = finisher["name"]
                    cursor.execute(
                        **load_lang.upsert_operating_copy(
                            app_name="gw2",
                            lang_tag=self.lang_tag.value,
                            original=finisher_name,
                        )
                    )
                    cursor.execute(
                        **upsert_finisher_name(
                            app_name="gw2",
                            finisher_id=finisher_id,
                            lang_tag=self.lang_tag.value,
                            original=finisher_name,
                        )
                    )

                cursor.execute(query="COMMIT")
                connection.commit()
                with self.output().open("w") as w_output:
                    w_output.write("ok")

            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                raise exception_instance


def upsert_finisher(finisher_id: int, icon: str, presentation_order: str) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.finisher AS target_finisher
USING (
  VALUES (%(finisher_id)s::integer, %(icon)s::text,
  %(presentation_order)s::integer)
) AS source_finisher (finisher_id, icon, presentation_order)
ON
  target_finisher.finisher_id = source_finisher.finisher_id
WHEN MATCHED
  AND target_finisher.icon != source_finisher.icon
  OR  target_finisher.presentation_order != source_finisher.presentation_order THEN
  UPDATE SET
    (icon, presentation_order) =
      (source_finisher.icon, source_finisher.presentation_order)
WHEN NOT MATCHED THEN
  INSERT (finisher_id, icon, presentation_order)
    VALUES (source_finisher.finisher_id,
      source_finisher.icon,
      source_finisher.presentation_order);
""",
        "params": {
            "finisher_id": finisher_id,
            "icon": icon,
            "presentation_order": presentation_order,
        },
    }


def upsert_finisher_detail(
    app_name: str, finisher_id: int, lang_tag: str, original: str
):
    return {
        "query": """
MERGE INTO gwapese.finisher_detail AS target_finisher_detail
USING (
VALUES (%(app_name)s::text, %(finisher_id)s::integer, %(lang_tag)s::text, %(original)s::text)) AS
  source_finisher_detail (app_name, finisher_id, lang_tag, original)
  ON target_finisher_detail.app_name = source_finisher_detail.app_name
  AND target_finisher_detail.lang_tag = source_finisher_detail.lang_tag
  AND target_finisher_detail.finisher_id = source_finisher_detail.finisher_id
WHEN MATCHED
  AND target_finisher_detail.original != source_finisher_detail.original THEN
  UPDATE SET
    original = source_finisher_detail.original
WHEN NOT MATCHED THEN
  INSERT (app_name, finisher_id, lang_tag, original)
    VALUES (source_finisher_detail.app_name,
      source_finisher_detail.finisher_id,
      source_finisher_detail.lang_tag,
      source_finisher_detail.original);""",
        "params": {
            "app_name": app_name,
            "finisher_id": finisher_id,
            "lang_tag": lang_tag,
            "original": original,
        },
    }


def upsert_finisher_name(app_name: str, finisher_id: int, lang_tag: str, original: str):
    return {
        "query": """
MERGE INTO gwapese.finisher_name AS target_finisher_name
USING (
VALUES (%(app_name)s::text, %(finisher_id)s::integer, %(lang_tag)s::text, %(original)s::text)) AS
  source_finisher_name (app_name, finisher_id, lang_tag, original)
  ON target_finisher_name.app_name = source_finisher_name.app_name
  AND target_finisher_name.lang_tag = source_finisher_name.lang_tag
  AND target_finisher_name.finisher_id = source_finisher_name.finisher_id
WHEN MATCHED
  AND target_finisher_name.original != source_finisher_name.original THEN
  UPDATE SET
    original = source_finisher_name.original
WHEN NOT MATCHED THEN
  INSERT (app_name, finisher_id, lang_tag, original)
    VALUES (source_finisher_name.app_name,
      source_finisher_name.finisher_id,
      source_finisher_name.lang_tag,
      source_finisher_name.original);""",
        "params": {
            "app_name": app_name,
            "finisher_id": finisher_id,
            "lang_tag": lang_tag,
            "original": original,
        },
    }
