import luigi
from os import path
from psycopg import sql

import common
import config
import load_color
import load_csv
import load_lang
import load_mount
import transform_color
import transform_mount_skin
import transform_mount


class WrapMountSkin(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        args = {"lang_tag": self.lang_tag}
        yield LoadMountSkin(**args)
        yield LoadMountSkinDyeSlot(**args)
        yield LoadMountSkinName(**args)


class LoadMountSkinTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    table = luigi.EnumParameter(enum=transform_mount_skin.MountSkinTable)

    def output(self):
        gwapo_config = config.gconfig()
        output_folder_name = "_".join(["load", self.table.value])
        return common.from_output_params(
            output_dir=path.join(gwapo_config.output_dir, output_folder_name),
            extract_datetime=gwapo_config.extract_datetime,
            params={"lang": self.lang_tag.value},
            ext="txt",
        )


class LoadMountSkin(LoadMountSkinTask):
    table = transform_mount_skin.MountSkinTable.MountSkin

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.mount_skin AS target_mount_skin
USING tempo_mount_skin AS source_mount_skin ON target_mount_skin.mount_id =
  source_mount_skin.mount_id
  AND target_mount_skin.mount_skin_id = source_mount_skin.mount_skin_id
WHEN MATCHED
  AND target_mount_skin.icon != source_mount_skin.icon THEN
  UPDATE SET
    icon = source_mount_skin.icon
WHEN NOT MATCHED THEN
  INSERT (icon, mount_id, mount_skin_id)
    VALUES (source_mount_skin.icon, source_mount_skin.mount_id,
      source_mount_skin.mount_skin_id);
"""
    )

    def requires(self):
        return {
            self.table.value: transform_mount_skin.TransformMountSkin(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_mount.MountTable.Mount.value: load_mount.LoadMount(
                lang_tag=self.lang_tag
            ),
        }


class LoadMountSkinDefault(LoadMountSkinTask):
    table = transform_mount.MountTable.MountSkinDefault

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.mount_skin_default
USING tempo_mount_skin_default
  ON gwapese.mount_skin_default.mount_id = tempo_mount_skin_default.mount_id
WHEN MATCHED
  AND gwapese.mount_skin_default.mount_skin_id != tempo_mount_skin_default.mount_skin_id THEN
  UPDATE SET
    mount_skin_id = tempo_mount_skin_default.mount_skin_id
WHEN NOT MATCHED THEN
  INSERT (mount_id, mount_skin_id)
    VALUES (tempo_mount_skin_default.mount_id,
      tempo_mount_skin_default.mount_skin_id);
"""
    )

    def requires(self):
        return {
            self.table.value: transform_mount.TransformMount(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_mount_skin.MountSkinTable.MountSkin.value: LoadMountSkin(
                lang_tag=self.lang_tag
            ),
        }


class LoadMountSkinDyeSlot(LoadMountSkinTask):
    table = transform_mount_skin.MountSkinTable.MountSkinDyeSlot

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.mount_skin_dye_slot
WHERE NOT EXISTS (
    SELECT
    FROM
      tempo_mount_skin_dye_slot
    WHERE
      gwapese.mount_skin_dye_slot.mount_skin_id = tempo_mount_skin_dye_slot.mount_skin_id
      AND gwapese.mount_skin_dye_slot.slot_index = tempo_mount_skin_dye_slot.slot_index);
"""
            ),
            sql.SQL(
                """
MERGE INTO gwapese.mount_skin_dye_slot AS target_mount_skin_dye_slot
USING tempo_mount_skin_dye_slot AS source_mount_skin_dye_slot ON
  target_mount_skin_dye_slot.mount_skin_id =
  source_mount_skin_dye_slot.mount_skin_id
  AND target_mount_skin_dye_slot.slot_index = source_mount_skin_dye_slot.slot_index
WHEN NOT MATCHED THEN
  INSERT (color_id, material, mount_skin_id, slot_index)
    VALUES (source_mount_skin_dye_slot.color_id,
      source_mount_skin_dye_slot.material,
      source_mount_skin_dye_slot.mount_skin_id,
      source_mount_skin_dye_slot.slot_index);
"""
            ),
        ]
    )

    def requires(self):
        return {
            self.table.value: transform_mount_skin.TransformMountSkin(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_color.ColorTable.ColorSample.value: load_color.LoadColorSample(
                lang_tag=self.lang_tag
            ),
            transform_mount_skin.MountSkinTable.MountSkin.value: LoadMountSkin(
                lang_tag=self.lang_tag
            ),
        }


class LoadMountSkinName(LoadMountSkinTask):
    table = transform_mount_skin.MountSkinTable.MountSkinName

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_mount_skin_name")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("mount_skin_name"),
                temp_table_name=sql.Identifier("tempo_mount_skin_name"),
                pk_name=sql.Identifier("mount_skin_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table.value: transform_mount_skin.TransformMountSkin(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_mount_skin.MountSkinTable.MountSkin.value: LoadMountSkin(
                lang_tag=self.lang_tag
            ),
            "lang": load_lang.LoadLang(),
        }
