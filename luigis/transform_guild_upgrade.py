import datetime
import enum
import luigi
from os import path

import common
import extract_batch
import transform_csv


class GuildUpgradeTable(enum.Enum):
    GuildUpgrade = "guild_upgrade"
    GuildUpgradeDescription = "guild_upgrade_description"
    GuildUpgradeName = "guild_upgrade_name"
    GuildUpgradePrerequisite = "guild_upgrade_prerequisite"


class TransformGuildUpgrade(transform_csv.TransformCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True)
    table = luigi.EnumParameter(enum=GuildUpgradeTable)

    def output(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.csv".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        target_dir = "_".join(["transform", self.table.value])
        target_path = path.join(
            self.output_dir,
            target_dir,
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        return extract_batch.ExtractBatchTask(
            extract_datetime=self.extract_datetime,
            json_schema_path="./schema/gw2/v2/guild/upgrades/index.json",
            output_dir=self.output_dir,
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/guild/upgrades",
        )

    def run(self, guild_upgrade):
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
                        "original": guild_upgrade["description"],
                    }
                ]
            case GuildUpgradeTable.GuildUpgradeName:
                return [
                    {
                        "app_name": "gw2",
                        "guild_upgrade_id": guild_upgrade_id,
                        "lang_tag": self.lang_tag.value,
                        "original": guild_upgrade["name"],
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

            case _:
                raise RuntimeError("Unexpected table name")
