import datetime
import luigi
from os import path
from psycopg import sql

import common
import config
import load_color
import load_csv
import load_lang
import transform_color
import transform_skiff


class WrapSkiff(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        args = {"lang_tag": self.lang_tag}
        yield LoadSkiff(**args)
        yield LoadSkiffDyeSlot(**args)
        yield LoadSkiffName(**args)


class LoadSkiffTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    table = luigi.EnumParameter(enum=transform_skiff.SkiffTable)

    def output(self):
        gwapo_config = config.gconfig()
        output_folder_name = "_".join(["load", self.table.value])
        return common.from_output_params(
            output_dir=path.join(gwapo_config.output_dir, output_folder_name),
            extract_datetime=gwapo_config.extract_datetime,
            params={"lang": self.lang_tag.value},
            ext="txt",
        )


class LoadSkiff(LoadSkiffTask):
    table = transform_skiff.SkiffTable.Skiff

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
            self.table.value: transform_skiff.TransformSkiff(
                lang_tag=self.lang_tag, table=self.table
            )
        }


class LoadSkiffDyeSlot(LoadSkiffTask):
    table = transform_skiff.SkiffTable.SkiffDyeSlot

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.skiff_dye_slot
WHERE NOT EXISTS (
    SELECT
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
            self.table.value: transform_skiff.TransformSkiff(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_color.ColorTable.ColorSample.value: load_color.LoadColorSample(
                lang_tag=self.lang_tag
            ),
            transform_skiff.SkiffTable.Skiff.value: LoadSkiff(lang_tag=self.lang_tag),
        }


class LoadSkiffName(LoadSkiffTask):
    table = transform_skiff.SkiffTable.SkiffName

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

    def requires(self):
        return {
            self.table.value: transform_skiff.TransformSkiff(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_skiff.SkiffTable.Skiff.value: LoadSkiff(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }