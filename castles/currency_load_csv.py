import luigi
from psycopg import sql

import common
import currency_transform_csv
import lang_load
from tasks import config
from tasks import load_csv


class WrapCurrency(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvCurrency(**args)
        yield LoadCsvCurrencyCategory(**args)
        yield LoadCsvCurrencyCurrencyCategory(**args)
        yield LoadCsvCurrencyDescription(**args)
        yield LoadCsvCurrencyName(**args)


class WrapCurrencyTranslate(luigi.WrapperTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        for lang_tag in common.LangTag:
            if lang_tag == self.original_lang_tag:
                continue
            yield LoadCsvCurrencyDescriptionTranslation(
                original_lang_tag=self.original_lang_tag,
                task_datetime=self.task_datetime,
                translation_lang_tag=lang_tag,
            )
            yield LoadCsvCurrencyNameTranslation(
                original_lang_tag=self.original_lang_tag,
                task_datetime=self.task_datetime,
                translation_lang_tag=lang_tag,
            )


class LoadCsvCurrencyTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
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
  FROM (
    SELECT DISTINCT ON
      (category_id) category_id
    FROM
      tempo_currency_category) AS currency_category_source
  WHERE gwapese.currency_category.category_id = currency_category_source.category_id
);
"""
            ),
            sql.SQL(
                """
MERGE INTO gwapese.currency_category
USING (
  SELECT DISTINCT ON
    (category_id) category_id
  FROM
    tempo_currency_category) AS currency_category_source
  ON gwapese.currency_category.category_id = currency_category_source.category_id
WHEN NOT MATCHED THEN
  INSERT (category_id)
    VALUES (currency_category_source.category_id);
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


class LoadCsvCurrencyCurrencyCategory(LoadCsvCurrencyTask):
    table = "currency_currency_category"

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.currency_currency_category
WHERE NOT EXISTS (
    SELECT
      1
    FROM
      tempo_currency_currency_category
    WHERE
      gwapese.currency_currency_category.category_id = tempo_currency_currency_category.category_id
      AND gwapese.currency_currency_category.currency_id = tempo_currency_currency_category.currency_id);
"""
            ),
            sql.SQL(
                """
MERGE INTO gwapese.currency_currency_category
USING tempo_currency_currency_category ON gwapese.currency_currency_category.category_id =
  tempo_currency_currency_category.category_id
  AND gwapese.currency_currency_category.currency_id = tempo_currency_currency_category.currency_id
WHEN NOT MATCHED THEN
  INSERT (category_id, currency_id)
    VALUES (tempo_currency_currency_category.category_id, tempo_currency_currency_category.currency_id);
"""
            ),
        ]
    )

    def requires(self):
        return {
            self.table: currency_transform_csv.TransformCsvCurrencyCurrencyCategory(
                lang_tag=self.lang_tag
            ),
            "currency": LoadCsvCurrency(lang_tag=self.lang_tag),
            "currency_category": LoadCsvCurrencyCategory(lang_tag=self.lang_tag),
        }


class LoadCsvCurrencyDescription(lang_load.LangLoadCopySourceTask):
    id_attributes = [("currency_id", sql.SQL("integer NOT NULL"))]
    table = "currency_description"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "currency"

    def requires(self):
        return {
            self.table: currency_transform_csv.TransformCsvCurrencyDescription(
                lang_tag=self.lang_tag
            ),
            "currency": LoadCsvCurrency(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }


class LoadCsvCurrencyDescriptionTranslation(lang_load.LangLoadCopyTargetTask):
    id_attributes = [("currency_id", sql.SQL("integer NOT NULL"))]
    table = "currency_description_context"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "currency"
    widget_table = "currency_description"

    def requires(self):
        return {
            self.table: currency_transform_csv.TransformCsvCurrencyDescriptionTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                translation_lang_tag=self.translation_lang_tag,
            ),
            "currency": LoadCsvCurrencyDescription(lang_tag=self.original_lang_tag),
        }


class LoadCsvCurrencyName(lang_load.LangLoadCopySourceTask):
    id_attributes = [("currency_id", sql.SQL("integer NOT NULL"))]
    table = "currency_name"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "currency"

    def requires(self):
        return {
            self.table: currency_transform_csv.TransformCsvCurrencyName(
                lang_tag=self.lang_tag
            ),
            "currency": LoadCsvCurrency(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }


class LoadCsvCurrencyNameTranslation(lang_load.LangLoadCopyTargetTask):
    id_attributes = [("currency_id", sql.SQL("integer NOT NULL"))]
    table = "currency_name_context"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "currency"
    widget_table = "currency_name"

    def requires(self):
        return {
            self.table: currency_transform_csv.TransformCsvCurrencyNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                translation_lang_tag=self.translation_lang_tag,
            ),
            "currency": LoadCsvCurrencyName(lang_tag=self.original_lang_tag),
        }
