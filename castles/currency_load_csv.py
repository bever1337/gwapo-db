import datetime
import luigi
from psycopg import sql

import common
from tasks import load_csv
import lang_load
import currency_transform_csv


class WrapCurrency(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvCurrency(**args)
        yield LoadCsvCurrencyCategory(**args)
        yield LoadCsvCurrencyDescription(**args)
        yield LoadCsvCurrencyName(**args)


class LoadCsvCurrencyTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "currency"


class LoadCsvCurrency(LoadCsvCurrencyTask):
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
            self.table: currency_transform_csv.TransformCsvCurrency(
                lang_tag=self.lang_tag
            )
        }


class LoadCsvCurrencyCategory(LoadCsvCurrencyTask):
    table = "currency_category"

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.currency_category
WHERE NOT EXISTS (
    SELECT
      1
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
            self.table: currency_transform_csv.TransformCsvCurrencyCategory(
                lang_tag=self.lang_tag
            ),
            "currency": LoadCsvCurrency(lang_tag=self.lang_tag),
        }


class LoadCsvCurrencyDescription(LoadCsvCurrencyTask):
    table = "currency_description"

    postcopy_sql = sql.Composed(
        [
            lang_load.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_currency_description")
            ),
            lang_load.merge_into_placed_copy.format(
                table_name=sql.Identifier("currency_description"),
                temp_table_name=sql.Identifier("tempo_currency_description"),
                pk_name=sql.Identifier("currency_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: currency_transform_csv.TransformCsvCurrencyDescription(
                lang_tag=self.lang_tag
            ),
            "currency": LoadCsvCurrency(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }


class LoadCsvCurrencyName(LoadCsvCurrencyTask):
    table = "currency_name"

    postcopy_sql = sql.Composed(
        [
            lang_load.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_currency_name")
            ),
            lang_load.merge_into_placed_copy.format(
                table_name=sql.Identifier("currency_name"),
                temp_table_name=sql.Identifier("tempo_currency_name"),
                pk_name=sql.Identifier("currency_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: currency_transform_csv.TransformCsvCurrencyName(
                lang_tag=self.lang_tag
            ),
            "currency": LoadCsvCurrency(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }
