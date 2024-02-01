import datetime
import luigi
from os import path
from psycopg import sql

import common
import load_csv
import load_lang
import transform_skiff


class LoadSkiffTask(load_csv.LoadCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)
    table = luigi.EnumParameter(enum=transform_skiff.SkiffTable)

    def output(self):
        output_folder_name = "_".join(["load", self.table.value])
        return common.from_output_params(
            output_dir=path.join(self.output_dir, output_folder_name),
            extract_datetime=self.extract_datetime,
            params={"lang": self.lang_tag.value},
            ext="txt",
        )

    def requires(self):
        return transform_skiff.TransformSkiff(
            extract_datetime=self.extract_datetime,
            lang_tag=self.lang_tag,
            output_dir=self.output_dir,
        )


class LoadSkiff(LoadSkiffTask):
    table = transform_skiff.SkiffTable.Skiff

    precopy_sql = load_csv.create_temporary_table.format(
        temp_table_name=sql.Identifier("tempo_skiff"),
        table_name=sql.Identifier("skiff"),
    )

    copy_sql = load_csv.copy_from_stdin.format(
        temp_table_name=sql.Identifier("tempo_skiff")
    )

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.skiff AS target_skiff
USING tempo_skiff AS source_skiff
ON
  target_skiff.skiff_id = source_skiff.skiff_id
WHEN MATCHED
  AND target_skiff.icon != source_skiff.icon THEN
  UPDATE SET
    icon = source_skiff.icon
WHEN NOT MATCHED THEN
  INSERT (icon, skiff_id)
    VALUES (source_skiff.icon,
      source_skiff.skiff_id);
"""
    )


class LoadSkiffDyeSlot(LoadSkiffTask):
    table = transform_skiff.SkiffTable.SkiffDyeSlot

    precopy_sql = load_csv.create_temporary_table.format(
        temp_table_name=sql.Identifier("tempo_skiff_dye_slot"),
        table_name=sql.Identifier("skiff_dye_slot"),
    )

    copy_sql = load_csv.copy_from_stdin.format(
        temp_table_name=sql.Identifier("tempo_skiff_dye_slot")
    )

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.skiff_dye_slot
WHERE NOT EXISTS (
  SELECT FROM tempo_skiff_dye_slot
  WHERE gwapese.skiff_dye_slot.skiff_id = tempo_skiff_dye_slot.skiff_id
    AND gwapese.skiff_dye_slot.slot_index = tempo_skiff_dye_slot.slot_index
);
"""
            ),
            sql.SQL(
                """
MERGE INTO gwapese.skiff_dye_slot AS target_skiff_dye_slot
USING tempo_skiff_dye_slot AS source_skiff_dye_slot
  ON target_skiff_dye_slot.skiff_id = source_skiff_dye_slot.skiff_id
  AND target_skiff_dye_slot.slot_index = source_skiff_dye_slot.slot_index
WHEN NOT MATCHED THEN
  INSERT (color_id, material, skiff_id, slot_index)
    VALUES (source_skiff_dye_slot.color_id,
      source_skiff_dye_slot.material,
      source_skiff_dye_slot.skiff_id,
      source_skiff_dye_slot.slot_index);
"""
            ),
        ]
    )


class LoadSkiffName(LoadSkiffTask):
    table = transform_skiff.SkiffTable.SkiffName

    precopy_sql = load_csv.create_temporary_table.format(
        temp_table_name=sql.Identifier("tempo_skiff_name"),
        table_name=sql.Identifier("skiff_name"),
    )

    copy_sql = load_csv.copy_from_stdin.format(
        temp_table_name=sql.Identifier("tempo_skiff_name")
    )

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_skiff_name")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("skiff_name"),
                temp_table_name=sql.Identifier("tempo_skiff_name"),
                pk_name=sql.Identifier("skiff_id"),
            ),
        ]
    )
