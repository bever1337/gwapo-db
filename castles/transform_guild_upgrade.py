import luigi

import common
import extract_batch
import transform_csv
import transform_lang


class TransformGuildUpgradeTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        return extract_batch.ExtractBatchTask(
            json_schema_path="./schema/gw2/v2/guild/upgrades/index.json",
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/guild/upgrades",
        )


class TransformGuildUpgrade(TransformGuildUpgradeTask):
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


class TransformGuildUpgradeDescription(TransformGuildUpgradeTask):
    def get_rows(self, guild_upgrade):
        guild_upgrade_description = guild_upgrade["description"]
        if guild_upgrade_description == "":
            return []
        return [
            {
                "app_name": "gw2",
                "guild_upgrade_id": guild_upgrade["id"],
                "lang_tag": self.lang_tag.value,
                "original": transform_lang.to_xhmtl_fragment(
                    guild_upgrade["description"]
                ),
            }
        ]


class TransformGuildUpgradeName(TransformGuildUpgradeTask):
    def get_rows(self, guild_upgrade):
        return [
            {
                "app_name": "gw2",
                "guild_upgrade_id": guild_upgrade["id"],
                "lang_tag": self.lang_tag.value,
                "original": transform_lang.to_xhmtl_fragment(guild_upgrade["name"]),
            }
        ]


class TransformGuildUpgradePrerequisite(TransformGuildUpgradeTask):
    def get_rows(self, guild_upgrade):
        guild_upgrade_id = guild_upgrade["id"]
        return [
            {
                "guild_upgrade_id": guild_upgrade_id,
                "prerequisite_guild_upgrade_id": prerequisite_id,
            }
            for prerequisite_id in guild_upgrade["prerequisites"]
        ]


class TransformGuildUpgradeCostCurrency(TransformGuildUpgradeTask):
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


class TransformGuildUpgradeCostItem(TransformGuildUpgradeTask):
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


class TransformGuildUpgradeCostWallet(TransformGuildUpgradeTask):
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
