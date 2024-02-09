import enum
import luigi
from os import path

import common
import config
import extract_batch
import transform_csv
import transform_lang


class GuildUpgradeTable(enum.Enum):
    GuildUpgrade = "guild_upgrade"
    GuildUpgradeDescription = "guild_upgrade_description"
    GuildUpgradeName = "guild_upgrade_name"
    GuildUpgradePrerequisite = "guild_upgrade_prerequisite"
    GuildUpgradeCostCurrency = "guild_upgrade_cost_currency"
    GuildUpgradeCostItem = "guild_upgrade_cost_item"
    GuildUpgradeCostWallet = "guild_upgrade_cost_wallet"


class TransformGuildUpgrade(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    table = luigi.EnumParameter(enum=GuildUpgradeTable)

    def output(self):
        gwapo_config = config.gconfig()
        output_folder_name = "_".join(["transform", self.table.value])
        return common.from_output_params(
            output_dir=path.join(gwapo_config.output_dir, output_folder_name),
            extract_datetime=gwapo_config.extract_datetime,
            params={"lang": self.lang_tag.value},
            ext="csv",
        )

    def requires(self):
        return extract_batch.ExtractBatchTask(
            json_schema_path="./schema/gw2/v2/guild/upgrades/index.json",
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/guild/upgrades",
        )

    def get_rows(self, guild_upgrade):
        guild_upgrade_id = guild_upgrade["id"]
        match self.table:
            case GuildUpgradeTable.GuildUpgrade:
                return [
                    {
                        "build_time": guild_upgrade["build_time"],
                        "experience": guild_upgrade["experience"],
                        "guild_upgrade_id": guild_upgrade_id,
                        "guild_upgrade_type": guild_upgrade["type"],
                        "icon": guild_upgrade["icon"],
                        "required_level": guild_upgrade["required_level"],
                    }
                ]
            case GuildUpgradeTable.GuildUpgradeDescription:
                guild_upgrade_description = guild_upgrade["description"]
                if guild_upgrade_description == "":
                    return []
                return [
                    {
                        "app_name": "gw2",
                        "guild_upgrade_id": guild_upgrade_id,
                        "lang_tag": self.lang_tag.value,
                        "original": transform_lang.to_xhmtl_fragment(
                            guild_upgrade["description"]
                        ),
                    }
                ]
            case GuildUpgradeTable.GuildUpgradeName:
                return [
                    {
                        "app_name": "gw2",
                        "guild_upgrade_id": guild_upgrade_id,
                        "lang_tag": self.lang_tag.value,
                        "original": transform_lang.to_xhmtl_fragment(
                            guild_upgrade["name"]
                        ),
                    }
                ]
            case GuildUpgradeTable.GuildUpgradePrerequisite:
                return [
                    {
                        "guild_upgrade_id": guild_upgrade_id,
                        "prerequisite_guild_upgrade_id": prerequisite_id,
                    }
                    for prerequisite_id in guild_upgrade["prerequisites"]
                ]
            case GuildUpgradeTable.GuildUpgradeCostCurrency:
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
            case GuildUpgradeTable.GuildUpgradeCostItem:
                return [
                    {
                        "guild_upgrade_id": guild_upgrade_id,
                        "item_id": cost["item_id"],
                        "quantity": cost["count"],
                    }
                    for cost in guild_upgrade["costs"]
                    if cost["type"] == "Item"
                ]
            case GuildUpgradeTable.GuildUpgradeCostWallet:
                return [
                    {
                        "currency_name": "Coin",
                        "guild_upgrade_id": guild_upgrade_id,
                        "quantity": cost["count"],
                    }
                    for cost in guild_upgrade["costs"]
                    if cost["type"] == "Coins"
                ]
            case _:
                raise RuntimeError("Unexpected table name")
