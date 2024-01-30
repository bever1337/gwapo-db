import datetime
import luigi
from os import path

import common
import load_csv
import transform_currency


class LoadCurrencyTask(load_csv.LoadCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)
    table = luigi.EnumParameter(enum=transform_currency.CurrencyTable)

    def output(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.txt".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        target_dir = "_".join(["load", self.table.value])
        target_path = path.join(
            self.output_dir,
            target_dir,
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        return transform_currency.TransformCurrency(
            extract_datetime=self.extract_datetime,
            lang_tag=self.lang_tag,
            output_dir=self.output_dir,
            table=self.table,
        )


class LoadCurrencyTable(LoadCurrencyTask):
    table = transform_currency.CurrencyTable.Currency

    precopy_sql = """
CREATE TEMPORARY TABLE tempo_currency (
  LIKE gwapese.currency
) ON COMMIT DROP;
ALTER TABLE tempo_currency
  DROP COLUMN sysrange_lower,
  DROP COLUMN sysrange_upper;"""

    copy_sql = """
COPY tempo_currency FROM STDIN (FORMAT 'csv', HEADER);"""

    postcopy_sql = """
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
      source_currency.presentation_order);"""


class LoadCurrencyCategoryTable(LoadCurrencyTask):
    table = transform_currency.CurrencyTable.CurrencyCategory

    precopy_sql = """
CREATE TEMPORARY TABLE tempo_currency_category (
  LIKE gwapese.currency_category
) ON COMMIT DROP;
ALTER TABLE tempo_currency_category
  DROP COLUMN sysrange_lower,
  DROP COLUMN sysrange_upper;"""

    copy_sql = """
COPY tempo_currency_category FROM STDIN (FORMAT 'csv', HEADER);"""

    postcopy_sql = """
DELETE FROM gwapese.currency_category
WHERE NOT EXISTS (
  SELECT FROM tempo_currency_category
  WHERE gwapese.currency_category.category = tempo_currency_category.category
    AND gwapese.currency_category.currency_id = tempo_currency_category.currency_id
);
MERGE INTO gwapese.currency_category
USING tempo_currency_category
ON gwapese.currency_category.category = tempo_currency_category.category
  AND gwapese.currency_category.currency_id = tempo_currency_category.currency_id
WHEN NOT MATCHED THEN
  INSERT (category, currency_id)
    VALUES (tempo_currency_category.category,
      tempo_currency_category.currency_id);"""


class LoadCurrencyDescriptionTable(LoadCurrencyTask):
    table = transform_currency.CurrencyTable.CurrencyDescription

    precopy_sql = """
CREATE TEMPORARY TABLE tempo_currency_description (
  LIKE gwapese.currency_description
) ON COMMIT DROP;
ALTER TABLE tempo_currency_description
  DROP COLUMN sysrange_lower,
  DROP COLUMN sysrange_upper;"""

    copy_sql = """
COPY tempo_currency_description FROM STDIN (FORMAT 'csv', HEADER);"""

    postcopy_sql = """
MERGE INTO gwapese.operating_copy AS target_operating_copy
USING tempo_currency_description AS source_operating_copy
ON target_operating_copy.app_name = source_operating_copy.app_name
  AND target_operating_copy.lang_tag = source_operating_copy.lang_tag
  AND target_operating_copy.original = source_operating_copy.original
WHEN NOT MATCHED THEN
    INSERT (app_name, lang_tag, original)
      VALUES (source_operating_copy.app_name,
        source_operating_copy.lang_tag,
        source_operating_copy.original);
MERGE INTO gwapese.currency_description AS target_currency_description
USING tempo_currency_description AS source_currency_description
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
      source_currency_description.original);"""


class LoadCurrencyNameTable(LoadCurrencyTask):
    table = transform_currency.CurrencyTable.CurrencyName

    precopy_sql = """
CREATE TEMPORARY TABLE tempo_currency_name (
  LIKE gwapese.currency_name
) ON COMMIT DROP;
ALTER TABLE tempo_currency_name
  DROP COLUMN sysrange_lower,
  DROP COLUMN sysrange_upper;"""

    copy_sql = """
COPY tempo_currency_name FROM STDIN (FORMAT 'csv', HEADER);"""

    postcopy_sql = """
MERGE INTO gwapese.operating_copy AS target_operating_copy
USING tempo_currency_name AS source_operating_copy
ON target_operating_copy.app_name = source_operating_copy.app_name
  AND target_operating_copy.lang_tag = source_operating_copy.lang_tag
  AND target_operating_copy.original = source_operating_copy.original
WHEN NOT MATCHED THEN
    INSERT (app_name, lang_tag, original)
      VALUES (source_operating_copy.app_name,
        source_operating_copy.lang_tag,
        source_operating_copy.original);
MERGE INTO gwapese.currency_name AS target_currency_name
USING tempo_currency_name AS source_currency_name
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
      source_currency_name.original);"""
