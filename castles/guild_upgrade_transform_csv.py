import datetime
import luigi

import common
import guild_upgrade_extract
from tasks import transform_csv


class TransformCsvGuildUpgradeTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "guild_upgrade"

    def requires(self):
        return guild_upgrade_extract.ExtractBatch(lang_tag=self.lang_tag)


class TransformCsvGuildUpgrade(TransformCsvGuildUpgradeTask):
    def get_rows(self, guild_upgrade):
        return [
            {
                "build_time": guild_upgrade["build_time"],
                "experience": guild_upgrade["experience"],
                "guild_upgrade_id": guild_upgrade["id"],
                "guild_upgrade_type": guild_upgrade["type"],
                "icon": guild_upgrade["icon"],
                "required_level": guild_upgrade["required_level"],
            }
        ]


class TransformCsvGuildUpgradeDescription(TransformCsvGuildUpgradeTask):
    def get_rows(self, guild_upgrade):
        guild_upgrade_description = guild_upgrade["description"]
        if guild_upgrade_description == "":
            return []
        return [
            {
                "app_name": "gw2",
                "guild_upgrade_id": guild_upgrade["id"],
                "lang_tag": self.lang_tag.value,
                "original": common.to_xhmtl_fragment(guild_upgrade["description"]),
            }
        ]


class TransformCsvGuildUpgradeName(TransformCsvGuildUpgradeTask):
    def get_rows(self, guild_upgrade):
        return [
            {
                "app_name": "gw2",
                "guild_upgrade_id": guild_upgrade["id"],
                "lang_tag": self.lang_tag.value,
                "original": common.to_xhmtl_fragment(guild_upgrade["name"]),
            }
        ]


class TransformCsvGuildUpgradePrerequisite(TransformCsvGuildUpgradeTask):
    def get_rows(self, guild_upgrade):
        guild_upgrade_id = guild_upgrade["id"]
        return [
            {
                "guild_upgrade_id": guild_upgrade_id,
                "prerequisite_guild_upgrade_id": prerequisite_id,
            }
            for prerequisite_id in guild_upgrade["prerequisites"]
        ]


class TransformCsvGuildUpgradeCostCurrency(TransformCsvGuildUpgradeTask):
    def get_rows(self, guild_upgrade):
        guild_upgrade_id = guild_upgrade["id"]
        return [
            *[
                {
                    "guild_currency_id": cost["name"],
                    "guild_upgrade_id": guild_upgrade_id,
                    "quantity": cost["count"],
                }
                for cost in guild_upgrade["costs"]
                if cost["type"] == "Currency"
            ],
            *[
                {
                    "guild_currency_id": "Favor",
                    "guild_upgrade_id": guild_upgrade_id,
                    "quantity": cost["count"],
                }
                for cost in guild_upgrade["costs"]
                if cost["type"] == "Collectible"
            ],
        ]


class TransformCsvGuildUpgradeCostItem(TransformCsvGuildUpgradeTask):
    def get_rows(self, guild_upgrade):
        guild_upgrade_id = guild_upgrade["id"]
        return [
            {
                "guild_upgrade_id": guild_upgrade_id,
                "item_id": cost["item_id"],
                "quantity": cost["count"],
            }
            for cost in guild_upgrade["costs"]
            if cost["type"] == "Item"
        ]


class TransformCsvGuildUpgradeCostWallet(TransformCsvGuildUpgradeTask):
    def get_rows(self, guild_upgrade):
        guild_upgrade_id = guild_upgrade["id"]
        return [
            {
                "currency_name": "Coin",
                "guild_upgrade_id": guild_upgrade_id,
                "quantity": cost["count"],
            }
            for cost in guild_upgrade["costs"]
            if cost["type"] == "Coins"
        ]
