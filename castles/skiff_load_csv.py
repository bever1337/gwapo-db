import datetime
import luigi
from psycopg import sql

import common
import color_load_csv
from tasks import load_csv
import lang_load
import skiff_transform_csv


class WrapSkiff(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvSkiff(**args)
        yield LoadCsvSkiffDyeSlot(**args)
        yield LoadCsvSkiffName(**args)


class LoadCsvSkiffTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
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


class LoadCsvSkiffName(LoadCsvSkiffTask):
    table = "skiff_name"

    postcopy_sql = sql.Composed(
        [
            lang_load.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_skiff_name")
            ),
            lang_load.merge_into_placed_copy.format(
                table_name=sql.Identifier("skiff_name"),
                temp_table_name=sql.Identifier("tempo_skiff_name"),
                pk_name=sql.Identifier("skiff_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: skiff_transform_csv.TransformCsvSkiffName(
                lang_tag=self.lang_tag
            ),
            "skiff": LoadCsvSkiff(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }
