import datetime
import json
import luigi
from os import path

import common
import load_lang
import transform_mini


class LoadMini(luigi.Task):
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
            "load_mini",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        return transform_mini.TransformMini(
            extract_datetime=self.extract_datetime, lang_tag=self.lang_tag
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
                for mini in json_input:
                    mini_id = mini["id"]
                    cursor.execute(
                        **upsert_mini(
                            icon=mini["icon"],
                            mini_id=mini_id,
                            presentation_order=mini["order"],
                        )
                    )

                    mini_name = mini["name"]
                    cursor.execute(
                        **load_lang.upsert_operating_copy(
                            app_name="gw2",
                            lang_tag=self.lang_tag.value,
                            original=mini_name,
                        )
                    )
                    cursor.execute(
                        **upsert_mini_name(
                            app_name="gw2",
                            mini_id=mini_id,
                            lang_tag=self.lang_tag.value,
                            original=mini_name,
                        )
                    )

                    mini_unlock = mini.get("unlock")
                    if mini_unlock != None:
                        cursor.execute(
                            **load_lang.upsert_operating_copy(
                                app_name="gw2",
                                lang_tag=self.lang_tag.value,
                                original=mini_unlock,
                            )
                        )
                        cursor.execute(
                            **upsert_mini_unlock(
                                app_name="gw2",
                                mini_id=mini_id,
                                lang_tag=self.lang_tag.value,
                                original=mini_unlock,
                            )
                        )

                cursor.execute(query="COMMIT")
                connection.commit()
                with self.output().open("w") as w_output:
                    w_output.write("ok")

            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                raise exception_instance


def upsert_mini(icon: str, mini_id: int, presentation_order: int) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.mini AS target_mini
USING (
  VALUES (%(icon)s::text, %(mini_id)s::integer, %(presentation_order)s::integer)
) AS source_mini (icon, mini_id, presentation_order)
ON
  target_mini.mini_id = source_mini.mini_id
WHEN MATCHED
  AND target_mini.icon != source_mini.icon 
  OR target_mini.presentation_order != source_mini.presentation_order THEN
  UPDATE SET
    (icon, presentation_order) = (source_mini.icon, source_mini.presentation_order)
WHEN NOT MATCHED THEN
  INSERT (icon, mini_id, presentation_order)
    VALUES (source_mini.icon,
      source_mini.mini_id,
      source_mini.presentation_order);
""",
        "params": {
            "icon": icon,
            "mini_id": mini_id,
            "presentation_order": presentation_order,
        },
    }


def upsert_mini_name(app_name: str, lang_tag: str, mini_id: int, original: str):
    return {
        "query": """
MERGE INTO gwapese.mini_name AS target_mini_name
USING (
VALUES (%(app_name)s::text, %(lang_tag)s::text, %(mini_id)s::integer, %(original)s::text)) AS
  source_mini_name (app_name, lang_tag, mini_id, original)
  ON target_mini_name.app_name = source_mini_name.app_name
  AND target_mini_name.lang_tag = source_mini_name.lang_tag
  AND target_mini_name.mini_id = source_mini_name.mini_id
WHEN MATCHED
  AND target_mini_name.original != source_mini_name.original THEN
  UPDATE SET
    original = source_mini_name.original
WHEN NOT MATCHED THEN
  INSERT (app_name, lang_tag, mini_id, original)
    VALUES (source_mini_name.app_name,
      source_mini_name.lang_tag,
      source_mini_name.mini_id,
      source_mini_name.original);""",
        "params": {
            "app_name": app_name,
            "lang_tag": lang_tag,
            "mini_id": mini_id,
            "original": original,
        },
    }


def upsert_mini_unlock(app_name: str, lang_tag: str, mini_id: int, original: str):
    return {
        "query": """
MERGE INTO gwapese.mini_unlock AS target_mini_unlock
USING (
VALUES (%(app_name)s::text, %(lang_tag)s::text, %(mini_id)s::integer, %(original)s::text)) AS
  source_mini_unlock (app_name, lang_tag, mini_id, original)
  ON target_mini_unlock.app_name = source_mini_unlock.app_name
  AND target_mini_unlock.lang_tag = source_mini_unlock.lang_tag
  AND target_mini_unlock.mini_id = source_mini_unlock.mini_id
WHEN MATCHED
  AND target_mini_unlock.original != source_mini_unlock.original THEN
  UPDATE SET
    original = source_mini_unlock.original
WHEN NOT MATCHED THEN
  INSERT (app_name, lang_tag, mini_id, original)
    VALUES (source_mini_unlock.app_name,
      source_mini_unlock.lang_tag,
      source_mini_unlock.mini_id,
      source_mini_unlock.original);""",
        "params": {
            "app_name": app_name,
            "lang_tag": lang_tag,
            "mini_id": mini_id,
            "original": original,
        },
    }
