import luigi
from psycopg import sql

import common
import color_load_csv
import lang_load
import skiff_transform_csv
from tasks import config
from tasks import load_csv


class WrapSkiff(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvSkiff(**args)
        yield LoadCsvSkiffDyeSlot(**args)
        yield LoadCsvSkiffName(**args)


class WrapSkiffTranslate(luigi.WrapperTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        for lang_tag in common.LangTag:
            if lang_tag == self.original_lang_tag:
                continue
            yield LoadCsvSkiffNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                task_datetime=self.task_datetime,
                translation_lang_tag=lang_tag,
            )


class LoadCsvSkiffTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "skiff"


class LoadCsvSkiff(LoadCsvSkiffTask):
    table = "skiff"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.skiff AS target_skiff
USING tempo_skiff AS source_skiff ON target_skiff.skiff_id = source_skiff.skiff_id
WHEN MATCHED
  AND target_skiff.icon != source_skiff.icon THEN
  UPDATE SET
    icon = source_skiff.icon
WHEN NOT MATCHED THEN
  INSERT (icon, skiff_id)
    VALUES (source_skiff.icon, source_skiff.skiff_id);
"""
    )

    def requires(self):
        return {
            self.table: skiff_transform_csv.TransformCsvSkiff(lang_tag=self.lang_tag)
        }


class LoadCsvSkiffDyeSlot(LoadCsvSkiffTask):
    table = "skiff_dye_slot"

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.skiff_dye_slot
WHERE NOT EXISTS (
    SELECT
      1
    FROM
      tempo_skiff_dye_slot
    WHERE
      gwapese.skiff_dye_slot.skiff_id = tempo_skiff_dye_slot.skiff_id
      AND gwapese.skiff_dye_slot.slot_index = tempo_skiff_dye_slot.slot_index);
"""
            ),
            sql.SQL(
                """
MERGE INTO gwapese.skiff_dye_slot AS target_skiff_dye_slot
USING tempo_skiff_dye_slot AS source_skiff_dye_slot ON
  target_skiff_dye_slot.skiff_id = source_skiff_dye_slot.skiff_id
  AND target_skiff_dye_slot.slot_index = source_skiff_dye_slot.slot_index
WHEN NOT MATCHED THEN
  INSERT (color_id, material, skiff_id, slot_index)
    VALUES (source_skiff_dye_slot.color_id, source_skiff_dye_slot.material,
      source_skiff_dye_slot.skiff_id, source_skiff_dye_slot.slot_index);
"""
            ),
        ]
    )

    def requires(self):
        return {
            self.table: skiff_transform_csv.TransformCsvSkiffDyeSlot(
                lang_tag=self.lang_tag
            ),
            "color_sample": color_load_csv.LoadCsvColorSample(lang_tag=self.lang_tag),
            "skiff": LoadCsvSkiff(lang_tag=self.lang_tag),
        }


class LoadCsvSkiffName(lang_load.LangLoadCopySourceTask):
    id_attributes = [("skiff_id", sql.SQL("integer NOT NULL"))]
    table = "skiff_name"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "skiff"

    def requires(self):
        return {
            self.table: skiff_transform_csv.TransformCsvSkiffName(
                lang_tag=self.lang_tag
            ),
            "skiff": LoadCsvSkiff(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }


class LoadCsvSkiffNameTranslation(lang_load.LangLoadCopyTargetTask):
    id_attributes = [("skiff_id", sql.SQL("integer NOT NULL"))]
    table = "skiff_name_context"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "skiff"
    widget_table = "skiff_name"

    def requires(self):
        return {
            self.table: skiff_transform_csv.TransformCsvSkiffNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                translation_lang_tag=self.translation_lang_tag,
            ),
            "_": LoadCsvSkiffName(lang_tag=self.original_lang_tag),
        }
