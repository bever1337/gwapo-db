import luigi
from psycopg import sql

import common
import currency_load_csv
import guild_currency_load
import guild_upgrade_transform_csv
import item_load_csv
import lang_load
from tasks import config
from tasks import load_csv


class WrapGuildUpgrade(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvGuildUpgrade(**args)
        yield LoadCsvGuildUpgradeDescription(**args)
        yield LoadCsvGuildUpgradeName(**args)
        yield LoadCsvGuildUpgradePrerequisite(**args)


class WrapGuildUpgradeTranslate(luigi.WrapperTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        for lang_tag in common.LangTag:
            if lang_tag == self.original_lang_tag:
                continue
            yield LoadCsvGuildUpgradeDescriptionTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                task_datetime=self.task_datetime,
                translation_lang_tag=lang_tag,
            )
            yield LoadCsvGuildUpgradeNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                task_datetime=self.task_datetime,
                translation_lang_tag=lang_tag,
            )


class LoadCsvGuildUpgradeTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "guild_upgrade"


class LoadCsvGuildUpgrade(LoadCsvGuildUpgradeTask):
    table = "guild_upgrade"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.guild_upgrade AS target_guild_upgrade
USING tempo_guild_upgrade AS source_guild_upgrade ON
  target_guild_upgrade.guild_upgrade_id = source_guild_upgrade.guild_upgrade_id
WHEN MATCHED
  AND (source_guild_upgrade.build_time, source_guild_upgrade.experience,
    source_guild_upgrade.guild_upgrade_type, source_guild_upgrade.icon,
    source_guild_upgrade.required_level) IS DISTINCT FROM
    (target_guild_upgrade.build_time, target_guild_upgrade.experience,
    target_guild_upgrade.guild_upgrade_type, target_guild_upgrade.icon,
    target_guild_upgrade.required_level) THEN
  UPDATE SET
    (build_time, experience, guild_upgrade_type, icon, required_level) =
      (source_guild_upgrade.build_time, source_guild_upgrade.experience,
      source_guild_upgrade.guild_upgrade_type, source_guild_upgrade.icon,
      source_guild_upgrade.required_level)
WHEN NOT MATCHED THEN
  INSERT (build_time, experience, guild_upgrade_id, guild_upgrade_type, icon,
    required_level)
    VALUES (source_guild_upgrade.build_time, source_guild_upgrade.experience,
      source_guild_upgrade.guild_upgrade_id,
      source_guild_upgrade.guild_upgrade_type, source_guild_upgrade.icon,
      source_guild_upgrade.required_level);
"""
    )

    def requires(self):
        return {
            self.table: guild_upgrade_transform_csv.TransformCsvGuildUpgrade(
                lang_tag=self.lang_tag
            )
        }


class LoadCsvGuildUpgradeDescription(lang_load.LangLoadCopySourceTask):
    id_attributes = [("guild_upgrade_id", sql.SQL("integer NOT NULL"))]
    table = "guild_upgrade_description"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "guild_upgrade"

    def requires(self):
        return {
            self.table: guild_upgrade_transform_csv.TransformCsvGuildUpgradeDescription(
                lang_tag=self.lang_tag
            ),
            "guild_upgrade": LoadCsvGuildUpgrade(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }


class LoadCsvGuildUpgradeDescriptionTranslation(lang_load.LangLoadCopyTargetTask):
    id_attributes = [("guild_upgrade_id", sql.SQL("integer NOT NULL"))]
    table = "guild_upgrade_description_context"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "guild_upgrade"
    widget_table = "guild_upgrade_description"

    def requires(self):
        return {
            self.table: guild_upgrade_transform_csv.TransformCsvGuildUpgradeDescriptionTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                translation_lang_tag=self.translation_lang_tag,
            ),
            "guild_upgrade_description": LoadCsvGuildUpgradeDescription(
                lang_tag=self.original_lang_tag
            ),
        }


class LoadCsvGuildUpgradeName(lang_load.LangLoadCopySourceTask):
    id_attributes = [("guild_upgrade_id", sql.SQL("integer NOT NULL"))]
    table = "guild_upgrade_name"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "guild_upgrade"

    def requires(self):
        return {
            self.table: guild_upgrade_transform_csv.TransformCsvGuildUpgradeName(
                lang_tag=self.lang_tag
            ),
            "guild_upgrade": LoadCsvGuildUpgrade(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }


class LoadCsvGuildUpgradeNameTranslation(lang_load.LangLoadCopyTargetTask):
    id_attributes = [("guild_upgrade_id", sql.SQL("integer NOT NULL"))]
    table = "guild_upgrade_name_context"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "guild_upgrade"
    widget_table = "guild_upgrade_name"

    def requires(self):
        return {
            self.table: guild_upgrade_transform_csv.TransformCsvGuildUpgradeNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                translation_lang_tag=self.translation_lang_tag,
            ),
            "guild_upgrade_name": LoadCsvGuildUpgradeName(
                lang_tag=self.original_lang_tag
            ),
        }


class LoadCsvGuildUpgradePrerequisite(LoadCsvGuildUpgradeTask):
    table = "guild_upgrade_prerequisite"

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.guild_upgrade_prerequisite
WHERE NOT EXISTS (
    SELECT
      1
    FROM
      tempo_guild_upgrade_prerequisite
    WHERE
      gwapese.guild_upgrade_prerequisite.guild_upgrade_id =
	tempo_guild_upgrade_prerequisite.guild_upgrade_id
      AND gwapese.guild_upgrade_prerequisite.prerequisite_guild_upgrade_id =
	tempo_guild_upgrade_prerequisite.prerequisite_guild_upgrade_id);
"""
            ),
            sql.SQL(
                """
MERGE INTO gwapese.guild_upgrade_prerequisite
USING tempo_guild_upgrade_prerequisite ON
  gwapese.guild_upgrade_prerequisite.prerequisite_guild_upgrade_id =
  tempo_guild_upgrade_prerequisite.prerequisite_guild_upgrade_id
  AND gwapese.guild_upgrade_prerequisite.guild_upgrade_id =
    tempo_guild_upgrade_prerequisite.guild_upgrade_id
WHEN NOT MATCHED THEN
  INSERT (guild_upgrade_id, prerequisite_guild_upgrade_id)
    VALUES (tempo_guild_upgrade_prerequisite.guild_upgrade_id,
      tempo_guild_upgrade_prerequisite.prerequisite_guild_upgrade_id);
"""
            ),
        ]
    )

    def requires(self):
        return {
            self.table: guild_upgrade_transform_csv.TransformCsvGuildUpgradePrerequisite(
                lang_tag=self.lang_tag
            ),
            "guild_upgrade": LoadCsvGuildUpgrade(lang_tag=self.lang_tag),
        }


class LoadCsvGuildUpgradeCostCurrency(LoadCsvGuildUpgradeTask):
    table = "guild_upgrade_cost_currency"

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.guild_upgrade_cost_currency
WHERE
  EXISTS (
    SELECT
      1
    FROM
      tempo_guild_upgrade_cost_currency
    WHERE
      gwapese.guild_upgrade_cost_currency.guild_upgrade_id = tempo_guild_upgrade_cost_currency.guild_upgrade_id)
  AND NOT EXISTS (
    SELECT
      1
    FROM
      tempo_guild_upgrade_cost_currency
    WHERE
      gwapese.guild_upgrade_cost_currency.guild_currency_id = tempo_guild_upgrade_cost_currency.guild_currency_id
      AND gwapese.guild_upgrade_cost_currency.guild_upgrade_id = tempo_guild_upgrade_cost_currency.guild_upgrade_id);
"""
            ),
            sql.SQL(
                """
MERGE INTO gwapese.guild_upgrade_cost_currency
USING tempo_guild_upgrade_cost_currency
  ON gwapese.guild_upgrade_cost_currency.guild_currency_id = tempo_guild_upgrade_cost_currency.guild_currency_id
  AND gwapese.guild_upgrade_cost_currency.guild_upgrade_id = tempo_guild_upgrade_cost_currency.guild_upgrade_id
WHEN MATCHED AND
  gwapese.guild_upgrade_cost_currency.quantity != tempo_guild_upgrade_cost_currency.quantity
THEN
  UPDATE SET quantity = tempo_guild_upgrade_cost_currency.quantity
WHEN NOT MATCHED THEN
  INSERT (guild_currency_id, guild_upgrade_id, quantity)
    VALUES (tempo_guild_upgrade_cost_currency.guild_currency_id,
      tempo_guild_upgrade_cost_currency.guild_upgrade_id,
      tempo_guild_upgrade_cost_currency.quantity);
"""
            ),
        ]
    )

    def requires(self):
        return {
            self.table: guild_upgrade_transform_csv.TransformCsvGuildUpgradeCostCurrency(
                lang_tag=self.lang_tag
            ),
            "guild_currency": guild_currency_load.GuildCurrencyLoad(),
            "guild_upgrade": LoadCsvGuildUpgrade(lang_tag=self.lang_tag),
        }


class LoadCsvGuildUpgradeCostItem(LoadCsvGuildUpgradeTask):
    table = "guild_upgrade_cost_item"

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.guild_upgrade_cost_item
WHERE
  EXISTS (
    SELECT
      1
    FROM
      tempo_guild_upgrade_cost_item
    WHERE
      gwapese.guild_upgrade_cost_item.guild_upgrade_id = tempo_guild_upgrade_cost_item.guild_upgrade_id)
  AND NOT EXISTS (
    SELECT
      1
    FROM
      tempo_guild_upgrade_cost_item
    WHERE
      gwapese.guild_upgrade_cost_item.guild_upgrade_id = tempo_guild_upgrade_cost_item.guild_upgrade_id
      AND gwapese.guild_upgrade_cost_item.item_id = tempo_guild_upgrade_cost_item.item_id);
"""
            ),
            sql.SQL(
                """
MERGE INTO gwapese.guild_upgrade_cost_item
USING tempo_guild_upgrade_cost_item
  ON gwapese.guild_upgrade_cost_item.guild_upgrade_id = tempo_guild_upgrade_cost_item.guild_upgrade_id
  AND gwapese.guild_upgrade_cost_item.item_id = tempo_guild_upgrade_cost_item.item_id
WHEN MATCHED AND
  gwapese.guild_upgrade_cost_item.quantity != tempo_guild_upgrade_cost_item.quantity
THEN
  UPDATE SET quantity = tempo_guild_upgrade_cost_item.quantity
WHEN NOT MATCHED THEN
  INSERT (guild_upgrade_id, item_id, quantity)
    VALUES (tempo_guild_upgrade_cost_item.guild_upgrade_id,
      tempo_guild_upgrade_cost_item.item_id,
      tempo_guild_upgrade_cost_item.quantity);
"""
            ),
        ]
    )

    def requires(self):
        return {
            self.table: guild_upgrade_transform_csv.TransformCsvGuildUpgradeCostItem(
                lang_tag=self.lang_tag
            ),
            "guild_upgrade": LoadCsvGuildUpgrade(lang_tag=self.lang_tag),
            "item": item_load_csv.LoadCsvItem(lang_tag=self.lang_tag),
        }


class LoadCsvGuildUpgradeCostWallet(LoadCsvGuildUpgradeTask):
    table = "guild_upgrade_cost_wallet"

    precopy_sql = sql.Composed(
        [
            sql.SQL(
                """
CREATE TEMPORARY TABLE tempo_guild_upgrade_cost_wallet (
  LIKE gwapese.guild_upgrade_cost_wallet
) ON COMMIT DROP;
"""
            ),
            sql.SQL(
                """
ALTER TABLE tempo_guild_upgrade_cost_wallet
  ADD COLUMN currency_name TEXT NOT NULL,
  DROP COLUMN currency_id,
  DROP COLUMN IF EXISTS sysrange_lower,
  DROP COLUMN IF EXISTS sysrange_upper;
"""
            ),
        ]
    )

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.guild_upgrade_cost_wallet
WHERE
  EXISTS (
    SELECT
      1
    FROM
      tempo_guild_upgrade_cost_wallet
    WHERE
      gwapese.guild_upgrade_cost_wallet.guild_upgrade_id = tempo_guild_upgrade_cost_wallet.guild_upgrade_id)
  AND NOT EXISTS (
    SELECT
      1
    FROM
      tempo_guild_upgrade_cost_wallet
    INNER JOIN
      gwapese.currency_name
    ON
      gwapese.currency_name.original = tempo_guild_upgrade_cost_wallet.currency_name
    WHERE
      gwapese.guild_upgrade_cost_wallet.currency_id = gwapese.currency_name.currency_id
      AND gwapese.guild_upgrade_cost_wallet.guild_upgrade_id = tempo_guild_upgrade_cost_wallet.guild_upgrade_id);
"""
            ),
            sql.SQL(
                """
MERGE INTO gwapese.guild_upgrade_cost_wallet
USING (
  SELECT
    gwapese.currency_name.currency_id,
    tempo_guild_upgrade_cost_wallet.guild_upgrade_id,
    tempo_guild_upgrade_cost_wallet.quantity
  FROM tempo_guild_upgrade_cost_wallet
  INNER JOIN
    gwapese.currency_name
  ON
    gwapese.currency_name.original = tempo_guild_upgrade_cost_wallet.currency_name
) AS source_guild_upgrade_cost_wallet
  ON gwapese.guild_upgrade_cost_wallet.currency_id = source_guild_upgrade_cost_wallet.currency_id
  AND gwapese.guild_upgrade_cost_wallet.guild_upgrade_id = source_guild_upgrade_cost_wallet.guild_upgrade_id
WHEN MATCHED AND
  gwapese.guild_upgrade_cost_wallet.quantity != source_guild_upgrade_cost_wallet.quantity
THEN
  UPDATE SET quantity = source_guild_upgrade_cost_wallet.quantity
WHEN NOT MATCHED THEN
  INSERT (currency_id, guild_upgrade_id, quantity)
    VALUES (source_guild_upgrade_cost_wallet.currency_id,
      source_guild_upgrade_cost_wallet.guild_upgrade_id,
      source_guild_upgrade_cost_wallet.quantity);
"""
            ),
        ]
    )

    def requires(self):
        return {
            self.table: guild_upgrade_transform_csv.TransformCsvGuildUpgradeCostWallet(
                lang_tag=self.lang_tag
            ),
            "currency_name": currency_load_csv.LoadCsvCurrencyName(
                lang_tag=self.lang_tag
            ),
            "guild_upgrade": LoadCsvGuildUpgrade(lang_tag=self.lang_tag),
        }
