import datetime
import luigi
from psycopg import sql

import common
import load_csv
import load_currency
import load_guild_currency
import load_item
import load_lang
import transform_guild_upgrade


class WrapGuildUpgrade(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_dateime": self.task_datetime}
        yield LoadGuildUpgrade(**args)
        yield LoadGuildUpgradeDescription(**args)
        yield LoadGuildUpgradeName(**args)
        yield LoadGuildUpgradePrerequisite(**args)


class LoadGuildUpgradeTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)


class LoadGuildUpgrade(LoadGuildUpgradeTask):
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
            self.table: transform_guild_upgrade.TransformGuildUpgrade(
                lang_tag=self.lang_tag
            )
        }


class LoadGuildUpgradeDescription(LoadGuildUpgradeTask):
    table = "guild_upgrade_description"

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_guild_upgrade_description")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("guild_upgrade_description"),
                temp_table_name=sql.Identifier("tempo_guild_upgrade_description"),
                pk_name=sql.Identifier("guild_upgrade_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: transform_guild_upgrade.TransformGuildUpgradeDescription(
                lang_tag=self.lang_tag
            ),
            "guild_upgrade": LoadGuildUpgrade(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }


class LoadGuildUpgradeName(LoadGuildUpgradeTask):
    table = "guild_upgrade_name"

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_guild_upgrade_name")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("guild_upgrade_name"),
                temp_table_name=sql.Identifier("tempo_guild_upgrade_name"),
                pk_name=sql.Identifier("guild_upgrade_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: transform_guild_upgrade.TransformGuildUpgradeName(
                lang_tag=self.lang_tag
            ),
            "guild_upgrade": LoadGuildUpgrade(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }


class LoadGuildUpgradePrerequisite(LoadGuildUpgradeTask):
    table = "guild_upgrade_prerequisite"

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.guild_upgrade_prerequisite
WHERE NOT EXISTS (
    SELECT
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
            self.table: transform_guild_upgrade.TransformGuildUpgradePrerequisite(
                lang_tag=self.lang_tag
            ),
            "guild_upgrade": LoadGuildUpgrade(lang_tag=self.lang_tag),
        }


class LoadGuildUpgradeCostCurrency(LoadGuildUpgradeTask):
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
            self.table: transform_guild_upgrade.TransformGuildUpgradeCostCurrency(
                lang_tag=self.lang_tag
            ),
            "guild_currency": load_guild_currency.LoadGuildCurrency(),
            "guild_upgrade": LoadGuildUpgrade(lang_tag=self.lang_tag),
        }


class LoadGuildUpgradeCostItem(LoadGuildUpgradeTask):
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
            self.table: transform_guild_upgrade.TransformGuildUpgradeCostItem(
                lang_tag=self.lang_tag
            ),
            "guild_upgrade": LoadGuildUpgrade(lang_tag=self.lang_tag),
            "item": load_item.LoadItem(lang_tag=self.lang_tag),
        }


class LoadGuildUpgradeCostWallet(LoadGuildUpgradeTask):
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
    LEFT JOIN
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
  LEFT JOIN
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
            self.table: transform_guild_upgrade.TransformGuildUpgradeCostWallet(
                lang_tag=self.lang_tag
            ),
            "currency_name": load_currency.LoadCurrencyName(lang_tag=self.lang_tag),
            "guild_upgrade": LoadGuildUpgrade(lang_tag=self.lang_tag),
        }
