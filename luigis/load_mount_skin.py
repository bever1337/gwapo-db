import datetime
import luigi
from os import path
from psycopg import sql

import common
import load_csv
import load_lang
import transform_mount_skin


class LoadMountSkinTask(load_csv.LoadCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)
    table = luigi.EnumParameter(enum=transform_mount_skin.MountSkinTable)

    def output(self):
        output_folder_name = "_".join(["load", self.table.value])
        return common.from_output_params(
            output_dir=path.join(self.output_dir, output_folder_name),
            extract_datetime=self.extract_datetime,
            params={"lang": self.lang_tag.value},
            ext="txt",
        )

    def requires(self):
        return transform_mount_skin.TransformMountSkin(
            extract_datetime=self.extract_datetime,
            lang_tag=self.lang_tag,
            output_dir=self.output_dir,
            table=self.table,
        )


class LoadMountSkin(LoadMountSkinTask):
    table = transform_mount_skin.MountSkinTable.MountSkin

    precopy_sql = load_csv.create_temporary_table.format(
        temp_table_name=sql.Identifier("tempo_mount_skin"),
        table_name=sql.Identifier("mount_skin"),
    )

    copy_sql = load_csv.copy_from_stdin.format(
        temp_table_name=sql.Identifier("tempo_mount_skin")
    )

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.mount_skin AS target_mount_skin
USING tempo_mount_skin AS source_mount_skin
ON
  target_mount_skin.mount_id = source_mount_skin.mount_id
  AND target_mount_skin.mount_skin_id = source_mount_skin.mount_skin_id
WHEN MATCHED
  AND target_mount_skin.icon != source_mount_skin.icon THEN
  UPDATE SET
    icon = source_mount_skin.icon
WHEN NOT MATCHED THEN
  INSERT (icon, mount_id, mount_skin_id)
    VALUES (source_mount_skin.icon,
      source_mount_skin.mount_id,  
      source_mount_skin.mount_skin_id);
"""
    )


class LoadMountSkinDyeSlot(LoadMountSkinTask):
    table = transform_mount_skin.MountSkinTable.MountSkinDyeSlot

    precopy_sql = load_csv.create_temporary_table.format(
        temp_table_name=sql.Identifier("tempo_mount_skin_dye_slot"),
        table_name=sql.Identifier("mount_skin_dye_slot"),
    )

    copy_sql = load_csv.copy_from_stdin.format(
        temp_table_name=sql.Identifier("tempo_mount_skin_dye_slot")
    )

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.mount_skin_dye_slot
WHERE NOT EXISTS (
  SELECT FROM tempo_mount_skin_dye_slot
  WHERE gwapese.mount_skin_dye_slot.mount_skin_id = tempo_mount_skin_dye_slot.mount_skin_id
    AND gwapese.mount_skin_dye_slot.slot_index = tempo_mount_skin_dye_slot.slot_index
);
"""
            ),
            sql.SQL(
                """
MERGE INTO gwapese.mount_skin_dye_slot AS target_mount_skin_dye_slot
USING tempo_mount_skin_dye_slot AS source_mount_skin_dye_slot
  ON target_mount_skin_dye_slot.mount_skin_id = source_mount_skin_dye_slot.mount_skin_id
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


class LoadMountSkinName(LoadMountSkinTask):
    table = transform_mount_skin.MountSkinTable.MountSkinName

    precopy_sql = load_csv.create_temporary_table.format(
        temp_table_name=sql.Identifier("tempo_mount_skin_name"),
        table_name=sql.Identifier("mount_skin_name"),
    )

    copy_sql = load_csv.copy_from_stdin.format(
        temp_table_name=sql.Identifier("tempo_mount_skin_name")
    )

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
