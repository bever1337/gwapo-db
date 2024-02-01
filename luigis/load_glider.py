import datetime
import luigi
from os import path
from psycopg import sql

import common
import load_csv
import load_lang
import transform_glider


class LoadGliderTask(load_csv.LoadCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)
    table = luigi.EnumParameter(enum=transform_glider.GliderTable)

    def output(self):
        output_folder_name = "_".join(["load", self.table.value])
        return common.from_output_params(
            output_dir=path.join(self.output_dir, output_folder_name),
            extract_datetime=self.extract_datetime,
            params={"lang": self.lang_tag.value},
            ext="txt",
        )

    def requires(self):
        return transform_glider.TransformGlider(
            extract_datetime=self.extract_datetime,
            lang_tag=self.lang_tag,
            output_dir=self.output_dir,
            table=self.table,
        )


class LoadGlider(LoadGliderTask):
    table = transform_glider.GliderTable.Glider

    precopy_sql = load_csv.create_temporary_table.format(
        temp_table_name=sql.Identifier("tempo_glider"),
        table_name=sql.Identifier("glider"),
    )

    copy_sql = load_csv.copy_from_stdin.format(
        temp_table_name=sql.Identifier("tempo_glider")
    )

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.glider AS target_glider
USING tempo_glider AS source_glider
ON
  target_glider.glider_id = source_glider.glider_id
WHEN MATCHED
  AND target_glider.icon != source_glider.icon
  OR target_glider.presentation_order != source_glider.presentation_order THEN
  UPDATE SET
    (icon, presentation_order) =
      (source_glider.icon, source_glider.presentation_order)
WHEN NOT MATCHED THEN
  INSERT (glider_id, icon, presentation_order)
    VALUES (source_glider.glider_id,
      source_glider.icon,
      source_glider.presentation_order);
"""
    )


class LoadGliderDescription(LoadGliderTask):
    table = transform_glider.GliderTable.GliderDescription

    precopy_sql = load_csv.create_temporary_table.format(
        temp_table_name=sql.Identifier("tempo_glider_description"),
        table_name=sql.Identifier("glider_description"),
    )

    copy_sql = load_csv.copy_from_stdin.format(
        temp_table_name=sql.Identifier("tempo_glider_description")
    )

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_glider_description")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("glider_description"),
                temp_table_name=sql.Identifier("tempo_glider_description"),
                pk_name=sql.Identifier("glider_id"),
            ),
        ]
    )


class LoadGliderDyeSlot(LoadGliderTask):
    table = transform_glider.GliderTable.GliderDyeSlot

    precopy_sql = load_csv.create_temporary_table.format(
        temp_table_name=sql.Identifier("tempo_glider_dye_slot"),
        table_name=sql.Identifier("glider_dye_slot"),
    )

    copy_sql = load_csv.copy_from_stdin.format(
        temp_table_name=sql.Identifier("tempo_glider_dye_slot")
    )

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.glider_dye_slot
WHERE NOT EXISTS (
  SELECT FROM tempo_glider_dye_slot
  WHERE gwapese.glider_dye_slot.glider_id = tempo_glider_dye_slot.glider_id
    AND gwapese.glider_dye_slot.slot_index = tempo_glider_dye_slot.slot_index
);
"""
            ),
            sql.SQL(
                """
MERGE INTO gwapese.glider_dye_slot AS target_glider_dye_slot
USING tempo_glider_dye_slot AS source_glider_dye_slot
  ON target_glider_dye_slot.glider_id = source_glider_dye_slot.glider_id
  AND target_glider_dye_slot.slot_index = source_glider_dye_slot.slot_index
WHEN NOT MATCHED THEN
  INSERT (color_id, glider_id, slot_index)
    VALUES (source_glider_dye_slot.color_id, source_glider_dye_slot.glider_id,
      source_glider_dye_slot.slot_index);
"""
            ),
        ]
    )


class LoadGliderName(LoadGliderTask):
    table = transform_glider.GliderTable.GliderName

    precopy_sql = load_csv.create_temporary_table.format(
        temp_table_name=sql.Identifier("tempo_glider_name"),
        table_name=sql.Identifier("glider_name"),
    )

    copy_sql = load_csv.copy_from_stdin.format(
        temp_table_name=sql.Identifier("tempo_glider_name")
    )

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_glider_name")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("glider_name"),
                temp_table_name=sql.Identifier("tempo_glider_name"),
                pk_name=sql.Identifier("glider_id"),
            ),
        ]
    )
