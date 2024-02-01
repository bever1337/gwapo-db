import datetime
import luigi
from os import path
from psycopg import sql

import common
import load_csv
import load_lang
import transform_guild_upgrade


class LoadGuildUpgradeTask(load_csv.LoadCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)
    table = luigi.EnumParameter(enum=transform_guild_upgrade.GuildUpgradeTable)

    def output(self):
        output_folder_name = "_".join(["load", self.table.value])
        return common.from_output_params(
            output_dir=path.join(self.output_dir, output_folder_name),
            extract_datetime=self.extract_datetime,
            params={"lang": self.lang_tag.value},
            ext="txt",
        )

    def requires(self):
        return transform_guild_upgrade.TransformGuildUpgrade(
            extract_datetime=self.extract_datetime,
            lang_tag=self.lang_tag,
            output_dir=self.output_dir,
            table=self.table,
        )


class LoadGuildUpgrade(LoadGuildUpgradeTask):
    table = transform_guild_upgrade.GuildUpgradeTable.GuildUpgrade

    precopy_sql = load_csv.create_temporary_table.format(
        temp_table_name=sql.Identifier("tempo_guild_upgrade"),
        table_name=sql.Identifier("guild_upgrade"),
    )

    copy_sql = load_csv.copy_from_stdin.format(
        temp_table_name=sql.Identifier("tempo_guild_upgrade")
    )

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.guild_upgrade AS target_guild_upgrade
USING tempo_guild_upgrade AS source_guild_upgrade
ON
  target_guild_upgrade.guild_upgrade_id = source_guild_upgrade.guild_upgrade_id
WHEN MATCHED
  AND (
    source_guild_upgrade.build_time,
    source_guild_upgrade.experience,
    source_guild_upgrade.guild_upgrade_type,
    source_guild_upgrade.icon,
    source_guild_upgrade.required_level
  ) IS DISTINCT FROM (
    target_guild_upgrade.build_time,
    target_guild_upgrade.experience,
    target_guild_upgrade.guild_upgrade_type,
    target_guild_upgrade.icon,
    target_guild_upgrade.required_level
  ) THEN
  UPDATE SET
    (build_time,
      experience,
      guild_upgrade_type,
      icon,
      required_level) =
      (source_guild_upgrade.build_time,
        source_guild_upgrade.experience,
        source_guild_upgrade.guild_upgrade_type,
        source_guild_upgrade.icon,
        source_guild_upgrade.required_level)
WHEN NOT MATCHED THEN
  INSERT (build_time,
    experience,
    guild_upgrade_id,
    guild_upgrade_type,
    icon,
    required_level)
    VALUES (source_guild_upgrade.build_time,
      source_guild_upgrade.experience,
      source_guild_upgrade.guild_upgrade_id,
      source_guild_upgrade.guild_upgrade_type,
      source_guild_upgrade.icon,
      source_guild_upgrade.required_level);
"""
    )


class LoadGuildUpgradeDescription(LoadGuildUpgradeTask):
    table = transform_guild_upgrade.GuildUpgradeTable.GuildUpgradeDescription

    precopy_sql = load_csv.create_temporary_table.format(
        temp_table_name=sql.Identifier("tempo_guild_upgrade_description"),
        table_name=sql.Identifier("guild_upgrade_description"),
    )

    copy_sql = load_csv.copy_from_stdin.format(
        temp_table_name=sql.Identifier("tempo_guild_upgrade_description")
    )

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


class LoadGuildUpgradeName(LoadGuildUpgradeTask):
    table = transform_guild_upgrade.GuildUpgradeTable.GuildUpgradeName

    precopy_sql = load_csv.create_temporary_table.format(
        temp_table_name=sql.Identifier("tempo_guild_upgrade_name"),
        table_name=sql.Identifier("guild_upgrade_name"),
    )

    copy_sql = load_csv.copy_from_stdin.format(
        temp_table_name=sql.Identifier("tempo_guild_upgrade_name")
    )

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


class LoadGuildUpgradePrerequisite(LoadGuildUpgradeTask):
    table = transform_guild_upgrade.GuildUpgradeTable.GuildUpgradePrerequisite

    precopy_sql = load_csv.create_temporary_table.format(
        temp_table_name=sql.Identifier("tempo_guild_upgrade_prerequisite"),
        table_name=sql.Identifier("guild_upgrade_prerequisite"),
    )

    copy_sql = load_csv.copy_from_stdin.format(
        temp_table_name=sql.Identifier("tempo_guild_upgrade_prerequisite")
    )

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.guild_upgrade_prerequisite
WHERE NOT EXISTS (
  SELECT FROM tempo_guild_upgrade_prerequisite
  WHERE gwapese.guild_upgrade_prerequisite.guild_upgrade_id
        = tempo_guild_upgrade_prerequisite.guild_upgrade_id
    AND gwapese.guild_upgrade_prerequisite.prerequisite_guild_upgrade_id
        = tempo_guild_upgrade_prerequisite.prerequisite_guild_upgrade_id
);
"""
            ),
            sql.SQL(
                """
MERGE INTO gwapese.guild_upgrade_prerequisite
USING tempo_guild_upgrade_prerequisite AS src
ON gwapese.guild_upgrade_prerequisite.prerequisite_guild_upgrade_id
    = tempo_guild_upgrade_prerequisite.prerequisite_guild_upgrade_id
  AND gwapese.guild_upgrade_prerequisite.guild_upgrade_id
    = tempo_guild_upgrade_prerequisite.guild_upgrade_id
WHEN NOT MATCHED THEN
  INSERT (guild_upgrade_id, prerequisite_guild_upgrade_id)
    VALUES (tempo_guild_upgrade_prerequisite.guild_upgrade_id,
      tempo_guild_upgrade_prerequisite.prerequisite_guild_upgrade_id);
"""
            ),
        ]
    )
