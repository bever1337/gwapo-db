import luigi
from os import path
from psycopg import sql

import common
import config
import load_csv
import load_lang
import load_profession
import load_race
import transform_item
import transform_profession
import transform_race


class WrapItem(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        args = {"lang_tag": self.lang_tag}
        yield LoadItem(**args)
        yield LoadItemDescription(**args)
        yield LoadItemFlag(**args)
        yield LoadItemGameType(**args)
        yield LoadItemName(**args)
        yield LoadItemProfessionRestriction(**args)
        yield LoadItemRaceRestriction(**args)
        yield LoadItemType(**args)
        yield LoadItemUpgrade(**args)


class LoadItemTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    table = luigi.EnumParameter(enum=transform_item.ItemTable)

    def output(self):
        gwapo_config = config.gconfig()
        output_folder_name = "_".join(["load", self.table.value])
        return common.from_output_params(
            output_dir=path.join(gwapo_config.output_dir, output_folder_name),
            extract_datetime=gwapo_config.extract_datetime,
            params={"lang": self.lang_tag.value},
            ext="txt",
        )


class LoadItem(LoadItemTask):
    table = transform_item.ItemTable.Item

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.item AS target_item
USING tempo_item AS source_item ON target_item.item_id = source_item.item_id
WHEN MATCHED
  AND source_item IS DISTINCT FROM (target_item.chat_link, target_item.icon,
    target_item.item_id, target_item.rarity, target_item.required_level,
    target_item.vendor_value) THEN
  UPDATE SET
    (chat_link, icon, rarity, required_level, vendor_value) =
      (source_item.chat_link, source_item.icon, source_item.rarity,
      source_item.required_level, source_item.vendor_value)
WHEN NOT MATCHED THEN
  INSERT (chat_link, icon, item_id, rarity, required_level, vendor_value)
    VALUES (source_item.chat_link, source_item.icon, source_item.item_id,
      source_item.rarity, source_item.required_level,
      source_item.vendor_value);
"""
    )

    def requires(self):
        return {
            self.table.value: transform_item.TransformItem(
                lang_tag=self.lang_tag, table=self.table
            )
        }


class LoadItemDescription(LoadItemTask):
    table = transform_item.ItemTable.ItemDescription

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_item_description")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("item_description"),
                temp_table_name=sql.Identifier("tempo_item_description"),
                pk_name=sql.Identifier("item_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table.value: transform_item.TransformItem(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_item.ItemTable.Item.value: LoadItem(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }


class LoadItemFlag(LoadItemTask):
    table = transform_item.ItemTable.ItemFlag

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.item_flag
WHERE NOT EXISTS (
    SELECT
    FROM
      tempo_item_flag
    WHERE
      gwapese.item_flag.flag = tempo_item_flag.flag
      AND gwapese.item_flag.item_id = tempo_item_flag.item_id);
"""
            ),
            sql.SQL(
                """
MERGE INTO gwapese.item_flag AS target_item_flag
USING tempo_item_flag AS source_item_flag ON target_item_flag.flag =
  source_item_flag.flag
  AND target_item_flag.item_id = source_item_flag.item_id
WHEN NOT MATCHED THEN
  INSERT (flag, item_id)
    VALUES (source_item_flag.flag, source_item_flag.item_id);
"""
            ),
        ]
    )

    def requires(self):
        return {
            self.table.value: transform_item.TransformItem(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_item.ItemTable.Item.value: LoadItem(lang_tag=self.lang_tag),
        }


class LoadItemGameType(LoadItemTask):
    table = transform_item.ItemTable.ItemGameType

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.item_game_type
WHERE NOT EXISTS (
    SELECT
    FROM
      tempo_item_game_type
    WHERE
      gwapese.item_game_type.game_type = tempo_item_game_type.game_type
      AND gwapese.item_game_type.item_id = tempo_item_game_type.item_id);
"""
            ),
            sql.SQL(
                """
MERGE INTO gwapese.item_game_type AS target_item_game_type
USING tempo_item_game_type AS source_item_game_type ON
  target_item_game_type.game_type = source_item_game_type.game_type
  AND target_item_game_type.item_id = source_item_game_type.item_id
WHEN NOT MATCHED THEN
  INSERT (game_type, item_id)
    VALUES (source_item_game_type.game_type, source_item_game_type.item_id);
"""
            ),
        ]
    )

    def requires(self):
        return {
            self.table.value: transform_item.TransformItem(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_item.ItemTable.Item.value: LoadItem(lang_tag=self.lang_tag),
        }


class LoadItemName(LoadItemTask):
    table = transform_item.ItemTable.ItemName

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_item_name")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("item_name"),
                temp_table_name=sql.Identifier("tempo_item_name"),
                pk_name=sql.Identifier("item_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table.value: transform_item.TransformItem(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_item.ItemTable.Item.value: LoadItem(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }


class LoadItemProfessionRestriction(LoadItemTask):
    table = transform_item.ItemTable.ItemProfessionRestriction

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.item_profession_restriction
WHERE NOT EXISTS (
    SELECT
    FROM
      tempo_item_profession_restriction
    WHERE
      gwapese.item_profession_restriction.item_id = tempo_item_profession_restriction.item_id
      AND gwapese.item_profession_restriction.profession_id =
	tempo_item_profession_restriction.profession_id);
"""
            ),
            sql.SQL(
                """
MERGE INTO gwapese.item_profession_restriction AS target_item_profession_restriction
USING tempo_item_profession_restriction AS source_item_profession_restriction
  ON target_item_profession_restriction.profession_id =
  source_item_profession_restriction.profession_id
  AND target_item_profession_restriction.item_id =
    source_item_profession_restriction.item_id
WHEN NOT MATCHED THEN
  INSERT (item_id, profession_id)
    VALUES (source_item_profession_restriction.item_id,
      source_item_profession_restriction.profession_id);
"""
            ),
        ]
    )

    def requires(self):
        return {
            self.table.value: transform_item.TransformItem(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_profession.ProfessionTable.Profession.value: load_profession.LoadProfession(
                lang_tag=self.lang_tag
            ),
            transform_item.ItemTable.Item.value: LoadItem(lang_tag=self.lang_tag),
        }


class LoadItemRaceRestriction(LoadItemTask):
    table = transform_item.ItemTable.ItemRaceRestriction

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.item_race_restriction
WHERE NOT EXISTS (
    SELECT
    FROM
      tempo_item_race_restriction
    WHERE
      gwapese.item_race_restriction.item_id = tempo_item_race_restriction.item_id
      AND gwapese.item_race_restriction.race_id = tempo_item_race_restriction.race_id);
"""
            ),
            sql.SQL(
                """
MERGE INTO gwapese.item_race_restriction AS target_item_race_restriction
USING tempo_item_race_restriction AS source_item_race_restriction ON
  target_item_race_restriction.item_id = source_item_race_restriction.item_id
  AND target_item_race_restriction.race_id = source_item_race_restriction.race_id
WHEN NOT MATCHED THEN
  INSERT (item_id, race_id)
    VALUES (source_item_race_restriction.item_id, source_item_race_restriction.race_id);
"""
            ),
        ]
    )

    def requires(self):
        return {
            self.table.value: transform_item.TransformItem(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_race.RaceTable.Race.value: load_race.LoadRace(
                lang_tag=self.lang_tag
            ),
            transform_item.ItemTable.Item.value: LoadItem(lang_tag=self.lang_tag),
        }


class LoadItemType(LoadItemTask):
    table = transform_item.ItemTable.ItemType

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.item_type AS target_item_type
USING tempo_item_type AS source_item_type ON target_item_type.item_id =
  source_item_type.item_id
WHEN NOT MATCHED THEN
  INSERT (item_id, item_type)
    VALUES (source_item_type.item_id, source_item_type.item_type);
"""
    )

    def requires(self):
        return {
            self.table.value: transform_item.TransformItem(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_item.ItemTable.Item.value: LoadItem(lang_tag=self.lang_tag),
        }


class LoadItemUpgrade(LoadItemTask):
    table = transform_item.ItemTable.ItemUpgrade

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.item_upgrade AS target_item_upgrade
USING (
  SELECT
    DISTINCT
      from_item_id, to_item_id, upgrade
    FROM
      tempo_item_upgrade
    WHERE
      EXISTS (
        SELECT
          1
        FROM
          gwapese.item
        WHERE
          gwapese.item.item_id = tempo_item_upgrade.from_item_id)
      AND EXISTS (
        SELECT
          1
        FROM
          gwapese.item
        WHERE
	      gwapese.item.item_id = tempo_item_upgrade.to_item_id)
) AS source_item_upgrade ON target_item_upgrade.from_item_id =
  source_item_upgrade.from_item_id
  AND target_item_upgrade.to_item_id = source_item_upgrade.to_item_id
  AND target_item_upgrade.upgrade = source_item_upgrade.upgrade
WHEN NOT MATCHED THEN
    INSERT
      (from_item_id, to_item_id, upgrade)
        VALUES (source_item_upgrade.from_item_id,
        source_item_upgrade.to_item_id,
	      source_item_upgrade.upgrade);
"""
    )

    def requires(self):
        return {
            self.table.value: transform_item.TransformItem(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_item.ItemTable.Item.value: LoadItem(lang_tag=self.lang_tag),
        }
