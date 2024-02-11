import datetime
import luigi
from psycopg import sql

import common
import load_csv
import load_lang
import transform_currency


class WrapCurrency(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCurrency(**args)
        yield LoadCurrencyCategory(**args)
        yield LoadCurrencyDescription(**args)
        yield LoadCurrencyName(**args)


class LoadCurrencyTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)


class LoadCurrency(LoadCurrencyTask):
    table = "currency"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.currency AS target_currency
USING tempo_currency AS source_currency ON target_currency.currency_id =
  source_currency.currency_id
WHEN MATCHED
  AND source_currency IS DISTINCT FROM (target_currency.currency_id,
    target_currency.deprecated, target_currency.icon,
    target_currency.presentation_order) THEN
  UPDATE SET
    (deprecated, icon, presentation_order) = (source_currency.deprecated,
      source_currency.icon, source_currency.presentation_order)
WHEN NOT MATCHED THEN
  INSERT (currency_id, deprecated, icon, presentation_order)
    VALUES (source_currency.currency_id, source_currency.deprecated,
      source_currency.icon, source_currency.presentation_order);
"""
    )

    def requires(self):
        return {
            self.table: transform_currency.TransformCurrency(lang_tag=self.lang_tag)
        }


class LoadCurrencyCategory(LoadCurrencyTask):
    table = "currency_category"

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.currency_category
WHERE NOT EXISTS (
    SELECT
    FROM
      tempo_currency_category
    WHERE
      gwapese.currency_category.category = tempo_currency_category.category
      AND gwapese.currency_category.currency_id = tempo_currency_category.currency_id);
"""
            ),
            sql.SQL(
                """
MERGE INTO gwapese.currency_category
USING tempo_currency_category ON gwapese.currency_category.category =
  tempo_currency_category.category
  AND gwapese.currency_category.currency_id = tempo_currency_category.currency_id
WHEN NOT MATCHED THEN
  INSERT (category, currency_id)
    VALUES (tempo_currency_category.category, tempo_currency_category.currency_id);
"""
            ),
        ]
    )

    def requires(self):
        return {
            self.table: transform_currency.TransformCurrencyCategory(
                lang_tag=self.lang_tag
            ),
            "currency": LoadCurrency(lang_tag=self.lang_tag),
        }


class LoadCurrencyDescription(LoadCurrencyTask):
    table = "currency_description"

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_currency_description")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("currency_description"),
                temp_table_name=sql.Identifier("tempo_currency_description"),
                pk_name=sql.Identifier("currency_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: transform_currency.TransformCurrencyDescription(
                lang_tag=self.lang_tag
            ),
            "currency": LoadCurrency(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }


class LoadCurrencyName(LoadCurrencyTask):
    table = "currency_name"

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_currency_name")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("currency_name"),
                temp_table_name=sql.Identifier("tempo_currency_name"),
                pk_name=sql.Identifier("currency_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: transform_currency.TransformCurrencyName(
                lang_tag=self.lang_tag
            ),
            "currency": LoadCurrency(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }
