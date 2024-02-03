import datetime
import luigi
from os import path
from psycopg import sql

import common
import load_csv
import load_lang
import transform_currency


class SeedCurrency(luigi.WrapperTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)

    def requires(self):
        args = {
            "extract_datetime": self.extract_datetime,
            "lang_tag": self.lang_tag,
            "output_dir": self.output_dir,
        }
        yield LoadCurrency(**args)
        yield LoadCurrencyCategory(**args)
        yield LoadCurrencyDescription(**args)
        yield LoadCurrencyName(**args)


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


class LoadCurrency(LoadCurrencyTask):
    table = transform_currency.CurrencyTable.Currency

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
            self.table.value: transform_currency.TransformCurrency(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
                table=self.table,
            )
        }


class LoadCurrencyCategory(LoadCurrencyTask):
    table = transform_currency.CurrencyTable.CurrencyCategory

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
            self.table.value: transform_currency.TransformCurrency(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
                table=self.table,
            ),
            transform_currency.CurrencyTable.Currency: LoadCurrency(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
            ),
        }


class LoadCurrencyDescription(LoadCurrencyTask):
    table = transform_currency.CurrencyTable.CurrencyDescription

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
            self.table.value: transform_currency.TransformCurrency(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
                table=self.table,
            ),
            transform_currency.CurrencyTable.Currency: LoadCurrency(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
            ),
        }


class LoadCurrencyName(LoadCurrencyTask):
    table = transform_currency.CurrencyTable.CurrencyName

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
            self.table.value: transform_currency.TransformCurrency(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
                table=self.table,
            ),
            transform_currency.CurrencyTable.Currency: LoadCurrency(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
            ),
        }
