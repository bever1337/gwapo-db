import datetime
import luigi
from os import path
from psycopg import sql

import common
import load_color
import load_csv
import load_lang
import load_mount
import transform_color
import transform_mount_skin
import transform_mount


class SeedMountSkin(luigi.WrapperTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)

    def requires(self):
        args = {
            "extract_datetime": self.extract_datetime,
            "lang_tag": self.lang_tag,
            "output_dir": self.output_dir,
        }
        yield LoadMountSkin(**args)
        yield LoadMountSkinDyeSlot(**args)
        yield LoadMountSkinName(**args)


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
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
                table=self.table,
            ),
            transform_mount.MountTable.Mount.value: load_mount.LoadMount(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
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
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
                table=self.table,
            ),
            transform_color.ColorTable.ColorSample.value: load_color.LoadColorSample(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
            ),
            transform_mount_skin.MountSkinTable.MountSkin.value: LoadMountSkin(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
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
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
                table=self.table,
            ),
            transform_mount_skin.MountSkinTable.MountSkin.value: LoadMountSkin(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
            ),
            "lang": load_lang.LoadLang(
                extract_datetime=self.extract_datetime, output_dir=self.output_dir
            ),
        }
