import datetime
import luigi
from os import path
from psycopg import sql

import common
from tasks import config


merge_into_operating_copy = sql.SQL(
    """
MERGE INTO gwapese.operating_copy AS target_operating_copy
USING (
  SELECT
    DISTINCT
      app_name, lang_tag, original
    FROM
      {table_name}) AS source_operating_copy ON target_operating_copy.app_name =
	source_operating_copy.app_name
  AND target_operating_copy.lang_tag = source_operating_copy.lang_tag
  AND target_operating_copy.original = source_operating_copy.original
WHEN NOT MATCHED THEN
  INSERT (app_name, lang_tag, original)
    VALUES (source_operating_copy.app_name, source_operating_copy.lang_tag,
      source_operating_copy.original);
"""
)


merge_into_placed_copy = sql.SQL(
    """
MERGE INTO gwapese.{table_name} AS merge_target
USING {temp_table_name} AS merge_source ON merge_target.app_name = merge_source.app_name
  AND merge_target.lang_tag = merge_source.lang_tag
  AND merge_target.{pk_name} = merge_source.{pk_name}
WHEN MATCHED
  AND merge_target.original != merge_source.original THEN
  UPDATE SET
    original = merge_source.original
WHEN NOT MATCHED THEN
  INSERT (app_name, lang_tag, original, {pk_name})
    VALUES (merge_source.app_name, merge_source.lang_tag,
      merge_source.original, merge_source.{pk_name});
"""
)


create_temporary_translation_table = sql.SQL(
    """
CREATE TEMPORARY TABLE tempo_translated_copy (
  LIKE gwapese.translated_copy
) ON COMMIT DROP;
"""
)


merge_into_translated_copy = sql.SQL(
    """
MERGE INTO gwapese.translated_copy AS target_translated_copy
USING (
  SELECT
    tempo_translated_copy.app_name,
    tempo_translated_copy.original_lang_tag,
    gwapese.color_name.original,
    tempo_translated_copy.translation_lang_tag,
    tempo_translated_copy.translation
  FROM
    tempo_translated_copy
  INNER JOIN
    gwapese.color_name
  ON
    tempo_translated_copy.app_name = gwapese.color_name.app_name
    AND tempo_translated_copy.original_lang_tag = gwapese.color_name.lang_tag
    AND tempo_translated_copy.color_id = gwapese.color_name.color_id
  ) AS source_translated_copy ON
    target_translated_copy.app_name = source_translated_copy.app_name
    AND target_translated_copy.original_lang_tag = source_translated_copy.original_lang_tag
    AND target_translated_copy.original = source_translated_copy.original
    AND target_translated_copy.translation_lang_tag = source_translated_copy.translation_lang_tag
  WHEN MATCHED
    AND target_translated_copy.translation !=
      source_translated_copy.translation THEN
    UPDATE SET
      translation = source_translated_copy.translation
  WHEN NOT MATCHED THEN
    INSERT (app_name,
      original_lang_tag,
      original,
      translation_lang_tag,
      translation)
      VALUES (source_translated_copy.app_name,
        source_translated_copy.original_lang_tag,
        source_translated_copy.original,
        source_translated_copy.translation_lang_tag,
        source_translated_copy.translation);
"""
)


class LangLoad(luigi.Task):
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "lang"

    def output(self):
        gwapo_config = config.gconfig()
        return luigi.LocalTarget(
            path=path.join(
                gwapo_config.output_dir,
                self.get_task_family(),
                path.extsep.join([self.task_id, "txt"]),
            )
        )

    def run(self):
        with (
            common.get_conn() as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute(query="BEGIN")
            try:
                cursor.execute(
                    query="""
MERGE INTO gwapese.lang AS target_lang
USING (
  SELECT
    lang_tag
  FROM
    unnest(%(lang_tags)s::text[]) AS lang_tag) AS source_lang ON
      target_lang.lang_tag = source_lang.lang_tag
WHEN NOT MATCHED THEN
  INSERT (lang_tag)
    VALUES (source_lang.lang_tag);
""",
                    params={
                        "lang_tags": [known_lang.value for known_lang in common.LangTag]
                    },
                )

                cursor.execute(
                    query=sql.SQL(
                        """
MERGE INTO gwapese.app AS target_app
USING (
  VALUES (%(app_name)s::text)) AS source_app (app_name) ON target_app.app_name =
    source_app.app_name
  WHEN NOT MATCHED THEN
    INSERT (app_name)
      VALUES (source_app.app_name);
"""
                    ),
                    params={"app_name": "gw2"},
                )
                cursor.execute(
                    query=sql.SQL(
                        """
MERGE INTO gwapese.operating_lang AS target_operating_lang
USING (
  VALUES (%(app_name)s::text, %(lang_tag)s::text)) AS source_operating_lang (app_name, lang_tag)
  ON target_operating_lang.app_name = source_operating_lang.app_name
  AND target_operating_lang.lang_tag = source_operating_lang.lang_tag
WHEN NOT MATCHED THEN
  INSERT (app_name, lang_tag)
    VALUES (source_operating_lang.app_name, source_operating_lang.lang_tag);
"""
                    ),
                    params={"app_name": "gw2", "lang_tag": "en"},
                )

                cursor.execute(query="COMMIT")
                connection.commit()
                with self.output().open("w") as w_output_file:
                    w_output_file.write("ok")
            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                raise exception_instance
