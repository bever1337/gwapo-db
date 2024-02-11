import datetime
import luigi
from psycopg import sql

import common
import load_color
import load_csv
import load_item
import load_lang
import transform_glider


class WrapGlider(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_dateime": self.task_datetime}
        yield LoadGlider(**args)
        yield LoadGliderDescription(**args)
        yield LoadGliderDyeSlot(**args)
        yield LoadGliderName(**args)


class LoadGliderTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)


class LoadGlider(LoadGliderTask):
    table = "glider"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.glider AS target_glider
USING tempo_glider AS source_glider ON target_glider.glider_id = source_glider.glider_id
WHEN MATCHED
  AND target_glider.icon != source_glider.icon
  OR target_glider.presentation_order != source_glider.presentation_order THEN
  UPDATE SET
    (icon, presentation_order) = (source_glider.icon, source_glider.presentation_order)
WHEN NOT MATCHED THEN
  INSERT (glider_id, icon, presentation_order)
    VALUES (source_glider.glider_id, source_glider.icon, source_glider.presentation_order);
"""
    )

    def requires(self):
        return {self.table: transform_glider.TransformGlider(lang_tag=self.lang_tag)}


class LoadGliderDescription(LoadGliderTask):
    table = "glider_description"

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

    def requires(self):
        return {
            self.table: transform_glider.TransformGliderDescription(
                lang_tag=self.lang_tag
            ),
            "glider": LoadGlider(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }


class LoadGliderDyeSlot(LoadGliderTask):
    table = "glider_dye_slot"

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.glider_dye_slot
WHERE NOT EXISTS (
    SELECT
    FROM
      tempo_glider_dye_slot
    WHERE
      gwapese.glider_dye_slot.glider_id = tempo_glider_dye_slot.glider_id
      AND gwapese.glider_dye_slot.slot_index = tempo_glider_dye_slot.slot_index);
"""
            ),
            sql.SQL(
                """
MERGE INTO gwapese.glider_dye_slot AS target_glider_dye_slot
USING tempo_glider_dye_slot AS source_glider_dye_slot ON
  target_glider_dye_slot.glider_id = source_glider_dye_slot.glider_id
  AND target_glider_dye_slot.slot_index = source_glider_dye_slot.slot_index
WHEN NOT MATCHED THEN
  INSERT (color_id, glider_id, slot_index)
    VALUES (source_glider_dye_slot.color_id, source_glider_dye_slot.glider_id,
      source_glider_dye_slot.slot_index);
"""
            ),
        ]
    )

    def requires(self):
        return {
            self.table: transform_glider.TransformGliderDyeSlot(lang_tag=self.lang_tag),
            "color": load_color.LoadColor(lang_tag=self.lang_tag),
            "glider": LoadGlider(lang_tag=self.lang_tag),
        }


class LoadGliderItem(LoadGliderTask):
    table = "glider_item"

    postcopy_sql = load_item.merge_into_item_reference.format(
        cross_table_name=sql.Identifier("glider_item"),
        table_name=sql.Identifier("glider"),
        temp_table_name=sql.Identifier("tempo_glider_item"),
        pk_name=sql.Identifier("glider_id"),
    )

    def requires(self):
        return {
            self.table: transform_glider.TransformGliderItem(lang_tag=self.lang_tag),
            "glider": LoadGlider(lang_tag=self.lang_tag),
            "item": load_item.LoadItem(lang_tag=self.lang_tag),
        }


class LoadGliderName(LoadGliderTask):
    table = "glider_name"

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

    def requires(self):
        return {
            self.table: transform_glider.TransformGliderName(lang_tag=self.lang_tag),
            "glider": LoadGlider(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }
