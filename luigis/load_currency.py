import datetime
import json
import luigi
from os import path

import common
import load_lang
import transform_currency


class LoadCurrency(luigi.Task):
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
            "load_currency",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        return transform_currency.TransformCurrency(
            extract_datetime=self.extract_datetime, lang_tag=self.lang_tag
        )

    def run(self):
        with (
            self.input().open("r") as r_input_file,
            common.get_conn() as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute(query="BEGIN")
            try:
                for currency_line in r_input_file:
                    currency = json.loads(currency_line)
                    currency_id = currency["id"]
                    cursor.execute(
                        **upsert_currency(
                            currency_id=currency_id,
                            deprecated=currency["deprecated"],
                            icon=currency["icon"],
                            presentation_order=currency["order"],
                        )
                    )
                    cursor.execute(
                        **prune_currency_categories(
                            categories=currency["categories"], currency_id=currency_id
                        )
                    )
                    cursor.execute(
                        **upsert_currency_categories(
                            categories=currency["categories"], currency_id=currency_id
                        )
                    )
                    cursor.execute(
                        **load_lang.upsert_operating_copy(
                            app_name="gw2",
                            lang_tag=self.lang_tag.value,
                            original=currency["description"],
                        )
                    )
                    cursor.execute(
                        **upsert_currency_description(
                            app_name="gw2",
                            currency_id=currency_id,
                            lang_tag=self.lang_tag.value,
                            original=currency["description"],
                        )
                    )
                    cursor.execute(
                        **load_lang.upsert_operating_copy(
                            app_name="gw2",
                            lang_tag=self.lang_tag.value,
                            original=currency["name"],
                        )
                    )
                    cursor.execute(
                        **upsert_currency_name(
                            app_name="gw2",
                            currency_id=currency_id,
                            lang_tag=self.lang_tag.value,
                            original=currency["name"],
                        )
                    )

                cursor.execute(query="COMMIT")
                connection.commit()
                with self.output().open("w") as w_output:
                    w_output.write("ok")

            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                raise exception_instance


def upsert_currency(
    currency_id: int, deprecated: bool, icon: str, presentation_order: str
) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.currency AS target_currency
USING (
  VALUES (%(currency_id)s::integer, %(deprecated)s::boolean,
  %(icon)s::text, %(presentation_order)s::integer)
) AS source_currency (currency_id, deprecated, icon, presentation_order)
ON
  target_currency.currency_id = source_currency.currency_id
WHEN MATCHED
  AND source_currency IS DISTINCT FROM (
    target_currency.currency_id,
    target_currency.deprecated,
    target_currency.icon,
    target_currency.presentation_order) THEN
  UPDATE SET
    (deprecated, icon, presentation_order) =
      (source_currency.deprecated,
        source_currency.icon,
        source_currency.presentation_order)
WHEN NOT MATCHED THEN
  INSERT (currency_id, deprecated, icon, presentation_order)
    VALUES (source_currency.currency_id,
      source_currency.deprecated,
      source_currency.icon,
      source_currency.presentation_order);
""",
        "params": {
            "currency_id": currency_id,
            "deprecated": deprecated,
            "icon": icon,
            "presentation_order": presentation_order,
        },
    }


def prune_currency_categories(categories: list[int], currency_id: int) -> dict:
    return {
        "query": """
DELETE FROM gwapese.currency_category
WHERE currency_id = %(currency_id)s::integer
  AND NOT category = ANY (%(categories)s::integer[]);
""",
        "params": {"categories": categories, "currency_id": currency_id},
    }


def upsert_currency_categories(categories: list[int], currency_id: int) -> dict:
    return {
        "query": """
MERGE INTO gwapese.currency_category AS target_currency_category
USING (
  SELECT
    %(currency_id)s::integer AS currency_id, category
  FROM
    unnest(%(categories)s::integer[]) AS category) AS source_currency_category
ON target_currency_category.category = source_currency_category.category
  AND target_currency_category.currency_id = source_currency_category.currency_id
WHEN NOT MATCHED THEN
  INSERT (category, currency_id)
    VALUES (source_currency_category.category, source_currency_category.currency_id);
""",
        "params": {"categories": categories, "currency_id": currency_id},
    }


def upsert_currency_description(
    app_name: str, currency_id: int, lang_tag: str, original: str
):
    return {
        "query": """
MERGE INTO gwapese.currency_description AS target_currency_description
USING (
VALUES (%s::text, %s::integer, %s::text, %s::text)) AS
  source_currency_description (app_name, currency_id, lang_tag, original)
  ON target_currency_description.app_name = source_currency_description.app_name
  AND target_currency_description.lang_tag = source_currency_description.lang_tag
  AND target_currency_description.currency_id = source_currency_description.currency_id
WHEN MATCHED
  AND target_currency_description.original != source_currency_description.original THEN
  UPDATE SET
    original = source_currency_description.original
WHEN NOT MATCHED THEN
  INSERT (app_name, currency_id, lang_tag, original)
    VALUES (source_currency_description.app_name,
      source_currency_description.currency_id,
      source_currency_description.lang_tag,
      source_currency_description.original);""",
        "params": (app_name, currency_id, lang_tag, original),
    }


def upsert_currency_name(app_name: str, currency_id: int, lang_tag: str, original: str):
    return {
        "query": """
MERGE INTO gwapese.currency_name AS target_currency_name
USING (
VALUES (%(app_name)s::text, %(currency_id)s::integer, %(lang_tag)s::text, %(original)s::text)) AS
  source_currency_name (app_name, currency_id, lang_tag, original)
  ON target_currency_name.app_name = source_currency_name.app_name
  AND target_currency_name.lang_tag = source_currency_name.lang_tag
  AND target_currency_name.currency_id = source_currency_name.currency_id
WHEN MATCHED
  AND target_currency_name.original != source_currency_name.original THEN
  UPDATE SET
    original = source_currency_name.original
WHEN NOT MATCHED THEN
  INSERT (app_name, currency_id, lang_tag, original)
    VALUES (source_currency_name.app_name,
      source_currency_name.currency_id,
      source_currency_name.lang_tag,
      source_currency_name.original);""",
        "params": {
            "app_name": app_name,
            "currency_id": currency_id,
            "lang_tag": lang_tag,
            "original": original,
        },
    }
