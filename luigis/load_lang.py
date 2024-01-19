import datetime
import luigi
from os import path

import common


class LoadLang(luigi.Task):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)

    def output(self):
        target_filename = "{timestamp:s}.txt".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
        )
        target_path = path.join(
            self.output_dir,
            "load_lang",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def run(self):
        with (
            common.get_conn() as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute(query="BEGIN")
            try:
                for known_lang in common.LangTag:
                    cursor.execute(**upsert_known_lang(lang_tag=known_lang.value))

                cursor.execute(**upsert_gw2_app(app_name="gw2"))
                cursor.execute(**upsert_operating_lang(app_name="gw2", lang_tag="en"))

                cursor.execute(query="COMMIT")
                connection.commit()
                with self.output().open("w") as w_output_file:
                    w_output_file.write("ok")
            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                raise exception_instance


def upsert_known_lang(lang_tag: str) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.lang AS target_lang
USING (
  VALUES (%s::text)
) AS source_lang (lang_tag)
ON
  target_lang.lang_tag = source_lang.lang_tag
WHEN NOT MATCHED THEN
  INSERT (lang_tag)
    VALUES (source_lang.lang_tag);
            """,
        "params": (lang_tag,),
    }


def upsert_gw2_app(app_name: str) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.app AS target_app
USING (
  VALUES (%s::text)
) AS source_app (app_name)
ON
    target_app.app_name = source_app.app_name
WHEN NOT MATCHED THEN
  INSERT (app_name)
    VALUES (source_app.app_name);""",
        "params": (app_name,),
    }


def upsert_operating_lang(app_name: str, lang_tag: str) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.operating_lang AS target_operating_lang
USING (
  VALUES (%s::text, %s::text)
) AS source_operating_lang (app_name, lang_tag)
ON
  target_operating_lang.app_name = source_operating_lang.app_name
  AND target_operating_lang.lang_tag = source_operating_lang.lang_tag
WHEN NOT MATCHED THEN
  INSERT (app_name, lang_tag)
    VALUES (source_operating_lang.app_name, source_operating_lang.lang_tag);""",
        "params": (app_name, lang_tag),
    }


def upsert_operating_copy(app_name: str, lang_tag: str, original: str) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.operating_copy AS target_operating_copy
USING (
  VALUES (%s::text, %s::text, %s::text)) AS source_operating_copy
    (app_name, lang_tag, original) ON
    target_operating_copy.app_name = source_operating_copy.app_name
    AND target_operating_copy.lang_tag = source_operating_copy.lang_tag
    AND target_operating_copy.original = source_operating_copy.original
  WHEN NOT MATCHED THEN
    INSERT (app_name, lang_tag, original)
      VALUES (source_operating_copy.app_name,
        source_operating_copy.lang_tag,
        source_operating_copy.original);""",
        "params": (app_name, lang_tag, original),
    }


def upsert_translated_copy(
    app_name: str,
    original_lang_tag: str,
    original: str,
    translation_lang_tag: str,
    translation: str,
) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.translated_copy AS target_translated_copy
USING (
  VALUES (%s::text, %s::text, %s::text, %s::text, %s::text)) AS source_translated_copy
    (app_name, original_lang_tag, original, translation_lang_tag, translation)
    ON target_translated_copy.app_name = source_translated_copy.app_name
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
        source_translated_copy.translation);""",
        "params": (
            app_name,
            original_lang_tag,
            original,
            translation_lang_tag,
            translation,
        ),
    }
