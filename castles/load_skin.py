import datetime
import luigi
from os import path
from psycopg import sql

import common
import config
import load_color
import load_csv
import load_lang
import load_race
import transform_color
import transform_race
import transform_skin


class WrapSkin(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        args = {"lang_tag": self.lang_tag}
        yield LoadSkin(**args)
        yield LoadSkinDescription(**args)
        yield LoadSkinFlag(**args)
        yield LoadSkinName(**args)
        yield LoadSkinRestriction(**args)
        yield LoadSkinType(**args)
        yield LoadSkinArmor(**args)
        yield LoadSkinArmorDyeSlot(**args)
        yield LoadSkinBack(**args)
        yield LoadSkinGathering(**args)
        yield LoadSkinWeapon(**args)


class LoadSkinTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    table = luigi.EnumParameter(enum=transform_skin.SkinTable)

    def output(self):
        gwapo_config = config.gconfig()
        output_folder_name = "_".join(["load", self.table.value])
        return common.from_output_params(
            output_dir=path.join(gwapo_config.output_dir, output_folder_name),
            extract_datetime=gwapo_config.extract_datetime,
            params={"lang": self.lang_tag.value},
            ext="txt",
        )


class LoadSkin(LoadSkinTask):
    table = transform_skin.SkinTable.Skin

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.skin AS target_skin
USING tempo_skin AS source_skin ON target_skin.skin_id = source_skin.skin_id
WHEN MATCHED
  AND target_skin.icon != source_skin.icon
  OR target_skin.rarity != source_skin.rarity THEN
  UPDATE SET
    (icon, rarity) = (source_skin.icon, source_skin.rarity)
WHEN NOT MATCHED THEN
  INSERT (icon, rarity, skin_id)
    VALUES (source_skin.icon, source_skin.rarity, source_skin.skin_id);
"""
    )

    def requires(self):
        return {
            self.table.value: transform_skin.TransformSkin(
                lang_tag=self.lang_tag, table=self.table
            )
        }


class LoadSkinDescription(LoadSkinTask):
    table = transform_skin.SkinTable.SkinDescription

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_skin_description")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("skin_description"),
                temp_table_name=sql.Identifier("tempo_skin_description"),
                pk_name=sql.Identifier("skin_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table.value: transform_skin.TransformSkin(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_skin.SkinTable.Skin.value: LoadSkin(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }


class LoadSkinFlag(LoadSkinTask):
    table = transform_skin.SkinTable.SkinFlag

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.skin_flag
WHERE NOT EXISTS (
    SELECT
    FROM
      tempo_skin_flag
    WHERE
      gwapese.skin_flag.flag = tempo_skin_flag.flag
      AND gwapese.skin_flag.skin_id = tempo_skin_flag.skin_id);
"""
            ),
            sql.SQL(
                """
MERGE INTO gwapese.skin_flag AS target_skin_flag
USING tempo_skin_flag AS source_skin_flag ON target_skin_flag.flag =
  source_skin_flag.flag
  AND target_skin_flag.skin_id = source_skin_flag.skin_id
WHEN NOT MATCHED THEN
  INSERT (flag, skin_id)
    VALUES (source_skin_flag.flag, source_skin_flag.skin_id);
"""
            ),
        ]
    )

    def requires(self):
        return {
            self.table.value: transform_skin.TransformSkin(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_skin.SkinTable.Skin.value: LoadSkin(lang_tag=self.lang_tag),
        }


class LoadSkinName(LoadSkinTask):
    table = transform_skin.SkinTable.SkinName

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_skin_name")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("skin_name"),
                temp_table_name=sql.Identifier("tempo_skin_name"),
                pk_name=sql.Identifier("skin_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table.value: transform_skin.TransformSkin(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_skin.SkinTable.Skin.value: LoadSkin(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }


class LoadSkinRestriction(LoadSkinTask):
    table = transform_skin.SkinTable.SkinRestriction

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.skin_restriction
WHERE NOT EXISTS (
    SELECT
    FROM
      tempo_skin_restriction
    WHERE
      gwapese.skin_restriction.restriction = tempo_skin_restriction.restriction
      AND gwapese.skin_restriction.skin_id = tempo_skin_restriction.skin_id);
"""
            ),
            sql.SQL(
                """
MERGE INTO gwapese.skin_restriction AS target_skin_restriction
USING tempo_skin_restriction AS source_skin_restriction ON
  target_skin_restriction.restriction = source_skin_restriction.restriction
  AND target_skin_restriction.skin_id = source_skin_restriction.skin_id
WHEN NOT MATCHED THEN
  INSERT (restriction, skin_id)
    VALUES (source_skin_restriction.restriction, source_skin_restriction.skin_id);
"""
            ),
        ]
    )

    def requires(self):
        return {
            self.table.value: transform_skin.TransformSkin(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_race.RaceTable.Race.value: load_race.LoadRace(
                lang_tag=self.lang_tag
            ),
            transform_skin.SkinTable.Skin.value: LoadSkin(lang_tag=self.lang_tag),
        }


class LoadSkinType(LoadSkinTask):
    table = transform_skin.SkinTable.SkinType

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.skin_type AS target_skin_type
USING tempo_skin_type AS source_skin_type ON target_skin_type.skin_id =
  source_skin_type.skin_id
WHEN NOT MATCHED THEN
  INSERT (skin_id, skin_type)
    VALUES (source_skin_type.skin_id, source_skin_type.skin_type);
"""
    )

    def requires(self):
        return {
            self.table.value: transform_skin.TransformSkin(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_skin.SkinTable.Skin.value: LoadSkin(lang_tag=self.lang_tag),
        }


class LoadSkinArmor(LoadSkinTask):
    table = transform_skin.SkinTable.SkinArmor

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.skin_armor AS target_skin_armor
USING tempo_skin_armor AS source_skin_armor ON target_skin_armor.skin_id =
  source_skin_armor.skin_id
WHEN MATCHED
  AND target_skin_armor.slot != source_skin_armor.slot
  OR target_skin_armor.weight_class != source_skin_armor.weight_class THEN
  UPDATE SET
    (slot, weight_class) = (source_skin_armor.slot, source_skin_armor.weight_class)
WHEN NOT MATCHED THEN
  INSERT (skin_id, slot, weight_class)
    VALUES (source_skin_armor.skin_id, source_skin_armor.slot,
      source_skin_armor.weight_class);
"""
    )

    def requires(self):
        return {
            self.table.value: transform_skin.TransformSkin(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_skin.SkinTable.SkinType.value: LoadSkinType(
                lang_tag=self.lang_tag
            ),
        }


class LoadSkinArmorDyeSlot(LoadSkinTask):
    table = transform_skin.SkinTable.SkinArmorDyeSlot

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.skin_armor_dye_slot
WHERE NOT EXISTS (
    SELECT
    FROM
      tempo_skin_armor_dye_slot
    WHERE
      gwapese.skin_armor_dye_slot.skin_id = tempo_skin_armor_dye_slot.skin_id
      AND gwapese.skin_armor_dye_slot.slot_index = tempo_skin_armor_dye_slot.slot_index);
"""
            ),
            sql.SQL(
                """
MERGE INTO gwapese.skin_armor_dye_slot AS target_dye_slot
USING tempo_skin_armor_dye_slot AS source_dye_slot ON target_dye_slot.skin_id =
  source_dye_slot.skin_id
  AND target_dye_slot.slot_index = source_dye_slot.slot_index
WHEN MATCHED
  AND target_dye_slot.color_id != source_dye_slot.color_id
  OR target_dye_slot.material != source_dye_slot.material THEN
  UPDATE SET
    (color_id, material) = (source_dye_slot.color_id, source_dye_slot.material)
WHEN NOT MATCHED THEN
  INSERT (color_id, material, skin_id, slot_index)
    VALUES (source_dye_slot.color_id, source_dye_slot.material,
      source_dye_slot.skin_id, source_dye_slot.slot_index);
"""
            ),
        ]
    )

    def requires(self):
        return {
            self.table.value: transform_skin.TransformSkin(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_color.ColorTable.ColorSample.value: load_color.LoadColorSample(
                lang_tag=self.lang_tag
            ),
            transform_skin.SkinTable.SkinArmor.value: LoadSkinArmor(
                lang_tag=self.lang_tag
            ),
        }


class LoadSkinBack(LoadSkinTask):
    table = transform_skin.SkinTable.SkinBack

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.skin_back AS target_skin_back
USING tempo_skin_back AS source_skin_back ON target_skin_back.skin_id =
  source_skin_back.skin_id
WHEN NOT MATCHED THEN
  INSERT (skin_id)
    VALUES (source_skin_back.skin_id);
"""
    )

    def requires(self):
        return {
            self.table.value: transform_skin.TransformSkin(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_skin.SkinTable.SkinType.value: LoadSkinType(
                lang_tag=self.lang_tag
            ),
        }


class LoadSkinGathering(LoadSkinTask):
    table = transform_skin.SkinTable.SkinGathering

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.skin_gathering AS target_skin_gathering
USING tempo_skin_gathering AS source_skin_gathering ON
  target_skin_gathering.skin_id = source_skin_gathering.skin_id
WHEN MATCHED
  AND target_skin_gathering.tool != source_skin_gathering.tool THEN
  UPDATE SET
    tool = source_skin_gathering.tool
WHEN NOT MATCHED THEN
  INSERT (skin_id, tool)
    VALUES (source_skin_gathering.skin_id, source_skin_gathering.tool);
"""
    )

    def requires(self):
        return {
            self.table.value: transform_skin.TransformSkin(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_skin.SkinTable.SkinType.value: LoadSkinType(
                lang_tag=self.lang_tag
            ),
        }


class LoadSkinWeapon(LoadSkinTask):
    table = transform_skin.SkinTable.SkinWeapon

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.skin_weapon AS target_skin_weapon
USING tempo_skin_weapon AS source_skin_weapon ON target_skin_weapon.skin_id =
  source_skin_weapon.skin_id
WHEN MATCHED
  AND target_skin_weapon.damage_type != source_skin_weapon.damage_type
  OR target_skin_weapon.weapon_type != source_skin_weapon.weapon_type THEN
  UPDATE SET
    (damage_type, weapon_type) = (source_skin_weapon.damage_type,
      source_skin_weapon.weapon_type)
WHEN NOT MATCHED THEN
  INSERT (damage_type, skin_id, weapon_type)
    VALUES (source_skin_weapon.damage_type, source_skin_weapon.skin_id,
      source_skin_weapon.weapon_type);
"""
    )

    def requires(self):
        return {
            self.table.value: transform_skin.TransformSkin(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_skin.SkinTable.SkinType.value: LoadSkinType(
                lang_tag=self.lang_tag
            ),
        }
