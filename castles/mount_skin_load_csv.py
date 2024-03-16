import luigi
from psycopg import sql

import common
import color_load_csv
import lang_load
import mount_load_csv
import mount_skin_transform_csv
import mount_transform_csv
from tasks import config
from tasks import load_csv


class WrapMountSkin(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvMountSkin(**args)
        yield LoadCsvMountSkinDyeSlot(**args)
        yield LoadCsvMountSkinName(**args)


class WrapMountSkinTranslate(luigi.WrapperTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        for lang_tag in common.LangTag:
            if lang_tag == self.original_lang_tag:
                continue
            yield LoadCsvMountSkinNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                task_datetime=self.task_datetime,
                translation_lang_tag=lang_tag,
            )


class LoadCsvMountSkinTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "mount_skin"


class LoadCsvMountSkin(LoadCsvMountSkinTask):
    table = "mount_skin"

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
            self.table: mount_skin_transform_csv.TransformCsvMountSkin(
                lang_tag=self.lang_tag
            ),
            "mount": mount_load_csv.LoadCsvMount(lang_tag=self.lang_tag),
        }


class LoadCsvMountSkinDefault(LoadCsvMountSkinTask):
    table = "mount_skin_default"

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
            self.table: mount_transform_csv.TransformCsvMountSkinDefault(
                lang_tag=self.lang_tag
            ),
            "mount_skin": LoadCsvMountSkin(lang_tag=self.lang_tag),
        }


class LoadCsvMountSkinDyeSlot(LoadCsvMountSkinTask):
    table = "mount_skin_dye_slot"

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.mount_skin_dye_slot
WHERE NOT EXISTS (
    SELECT
      1
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
            self.table: mount_skin_transform_csv.TransformCsvMountSkinDyeSlot(
                lang_tag=self.lang_tag
            ),
            "color_sample": color_load_csv.LoadCsvColorSample(lang_tag=self.lang_tag),
            "mount_skin": LoadCsvMountSkin(lang_tag=self.lang_tag),
        }


class LoadCsvMountSkinName(lang_load.LangLoadCopySourceTask):
    id_attributes = [("mount_skin_id", sql.SQL("integer NOT NULL"))]
    table = "mount_skin_name"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "mount_skin"

    def requires(self):
        return {
            self.table: mount_skin_transform_csv.TransformCsvMountSkinName(
                lang_tag=self.lang_tag
            ),
            "mount_skin": LoadCsvMountSkin(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }


class LoadCsvMountSkinNameTranslation(lang_load.LangLoadCopyTargetTask):
    id_attributes = [("mount_skin_id", sql.SQL("integer NOT NULL"))]
    table = "mount_skin_name_context"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "mount_skin"
    widget_table = "mount_skin_name"

    def requires(self):
        return {
            self.table: mount_skin_transform_csv.TransformCsvMountSkinNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                translation_lang_tag=self.translation_lang_tag,
            ),
            "_": LoadCsvMountSkinName(lang_tag=self.original_lang_tag),
        }
