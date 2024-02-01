import datetime
import luigi
from os import path
from psycopg import sql

import common
import load_csv
import load_lang
import transform_currency


class LoadCurrencyTask(load_csv.LoadCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)
    table = luigi.EnumParameter(enum=transform_currency.CurrencyTable)

    def output(self):
        output_folder_name = "_".join(["load", self.table.value])
        return common.from_output_params(
            output_dir=path.join(self.output_dir, output_folder_name),
            extract_datetime=self.extract_datetime,
            params={"lang": self.lang_tag.value},
            ext="txt",
        )

    def requires(self):
        return transform_currency.TransformCurrency(
            extract_datetime=self.extract_datetime,
            lang_tag=self.lang_tag,
            output_dir=self.output_dir,
            table=self.table,
        )


class LoadCurrency(LoadCurrencyTask):
    table = transform_currency.CurrencyTable.Currency

    precopy_sql = load_csv.create_temporary_table.format(
        temp_table_name=sql.Identifier("tempo_currency"),
        table_name=sql.Identifier("currency"),
    )

    copy_sql = load_csv.copy_from_stdin.format(
        temp_table_name=sql.Identifier("tempo_currency")
    )

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.currency AS target_currency
USING tempo_currency AS source_currency
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
"""
    )


class LoadCurrencyCategory(LoadCurrencyTask):
    table = transform_currency.CurrencyTable.CurrencyCategory

    precopy_sql = load_csv.create_temporary_table.format(
        temp_table_name=sql.Identifier("tempo_currency_category"),
        table_name=sql.Identifier("currency_category"),
    )

    copy_sql = load_csv.copy_from_stdin.format(
        temp_table_name=sql.Identifier("tempo_currency_category")
    )

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.currency_category
WHERE NOT EXISTS (
  SELECT FROM tempo_currency_category
  WHERE gwapese.currency_category.category = tempo_currency_category.category
    AND gwapese.currency_category.currency_id = tempo_currency_category.currency_id
);
"""
            ),
            sql.SQL(
                """
MERGE INTO gwapese.currency_category
USING tempo_currency_category
ON gwapese.currency_category.category = tempo_currency_category.category
  AND gwapese.currency_category.currency_id = tempo_currency_category.currency_id
WHEN NOT MATCHED THEN
  INSERT (category, currency_id)
    VALUES (tempo_currency_category.category,
      tempo_currency_category.currency_id);
"""
            ),
        ]
    )


class LoadCurrencyDescription(LoadCurrencyTask):
    table = transform_currency.CurrencyTable.CurrencyDescription

    precopy_sql = load_csv.create_temporary_table.format(
        temp_table_name=sql.Identifier("tempo_currency_description"),
        table_name=sql.Identifier("currency_description"),
    )

    copy_sql = load_csv.copy_from_stdin.format(
        temp_table_name=sql.Identifier("tempo_currency_description")
    )

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


class LoadCurrencyName(LoadCurrencyTask):
    table = transform_currency.CurrencyTable.CurrencyName

    precopy_sql = load_csv.create_temporary_table.format(
        temp_table_name=sql.Identifier("tempo_currency_name"),
        table_name=sql.Identifier("currency_name"),
    )

    copy_sql = load_csv.copy_from_stdin.format(
        temp_table_name=sql.Identifier("tempo_currency_name")
    )

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
