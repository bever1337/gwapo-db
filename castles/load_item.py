import luigi
from psycopg import sql

import common
import load_csv
import load_lang
import load_profession
import load_race
import transform_item

merge_into_item_reference = sql.SQL(
    """
MERGE INTO gwapese.{cross_table_name} AS target_item_reference
USING (
  SELECT
    {pk_name},
    item_id
  FROM
    {temp_table_name}
  WHERE
    EXISTS (
      SELECT
        1
      FROM
        gwapese.{table_name}
      WHERE
        gwapese.{table_name}.{pk_name} = {temp_table_name}.{pk_name})
    AND EXISTS (
      SELECT
        1
      FROM
        gwapese.item
      WHERE
        gwapese.item.item_id = {temp_table_name}.item_id)
) AS source_item_reference ON target_item_reference.{pk_name} = source_item_reference.{pk_name}
  AND target_item_reference.item_id = source_item_reference.item_id
WHEN NOT MATCHED THEN
  INSERT ({pk_name}, item_id)
    VALUES (source_item_reference.{pk_name}, source_item_reference.item_id);
"""
)


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


class LoadItem(LoadItemTask):
    table = "item"

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
        return {self.table: transform_item.TransformItem(lang_tag=self.lang_tag)}


class LoadItemDescription(LoadItemTask):
    table = "item_description"

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
            self.table: transform_item.TransformItemDescription(lang_tag=self.lang_tag),
            "item": LoadItem(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }


class LoadItemFlag(LoadItemTask):
    table = "item_flag"

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
            self.table: transform_item.TransformItemFlag(lang_tag=self.lang_tag),
            "item": LoadItem(lang_tag=self.lang_tag),
        }


class LoadItemGameType(LoadItemTask):
    table = "item_game_type"

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
            self.table: transform_item.TransformItemGameType(lang_tag=self.lang_tag),
            "item": LoadItem(lang_tag=self.lang_tag),
        }


class LoadItemName(LoadItemTask):
    table = "item_name"

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
            self.table: transform_item.TransformItemName(lang_tag=self.lang_tag),
            "item": LoadItem(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }


class LoadItemProfessionRestriction(LoadItemTask):
    table = "item_profession_restriction"

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
            self.table: transform_item.TransformItemRestrictionProfession(
                lang_tag=self.lang_tag
            ),
            "profession": load_profession.LoadProfession(lang_tag=self.lang_tag),
            "item": LoadItem(lang_tag=self.lang_tag),
        }


class LoadItemRaceRestriction(LoadItemTask):
    table = "item_race_restriction"

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
            self.table: transform_item.TransformItemRestrictionRace(
                lang_tag=self.lang_tag
            ),
            "race": load_race.LoadRace(lang_tag=self.lang_tag),
            "item": LoadItem(lang_tag=self.lang_tag),
        }


class LoadItemType(LoadItemTask):
    table = "item_type"

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
            self.table: transform_item.TransformItemType(lang_tag=self.lang_tag),
            "item": LoadItem(lang_tag=self.lang_tag),
        }


class LoadItemUpgrade(LoadItemTask):
    table = "item_upgrade"

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
            self.table: transform_item.TransformItemUpgrade(lang_tag=self.lang_tag),
            "item": LoadItem(lang_tag=self.lang_tag),
        }
