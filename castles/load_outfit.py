import datetime
import luigi
from psycopg import sql

import common
import load_csv
import load_item
import load_lang
import transform_outfit


class WrapOutfit(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadOutfit(**args)
        yield LoadOutfitName(**args)


class LoadOutfitTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)


class LoadOutfit(LoadOutfitTask):
    table = "outfit"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.outfit AS target_outfit
USING tempo_outfit AS source_outfit ON target_outfit.outfit_id = source_outfit.outfit_id
WHEN MATCHED
  AND target_outfit.icon != source_outfit.icon THEN
  UPDATE SET
    icon = source_outfit.icon
WHEN NOT MATCHED THEN
  INSERT (icon, outfit_id)
    VALUES (source_outfit.icon, source_outfit.outfit_id);
"""
    )

    def requires(self):
        return {self.table: transform_outfit.TransformOutfit(lang_tag=self.lang_tag)}


class LoadOutfitItem(LoadOutfitTask):
    table = "outfit_item"

    postcopy_sql = load_item.merge_into_item_reference.format(
        cross_table_name=sql.Identifier("outfit_item"),
        table_name=sql.Identifier("outfit"),
        temp_table_name=sql.Identifier("tempo_outfit_item"),
        pk_name=sql.Identifier("outfit_id"),
    )

    def requires(self):
        return {
            self.table: transform_outfit.TransformOutfitItem(lang_tag=self.lang_tag),
            "outfit": LoadOutfit(lang_tag=self.lang_tag),
            "item": load_item.LoadItem(lang_tag=self.lang_tag),
        }


class LoadOutfitName(LoadOutfitTask):
    table = "outfit_name"

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_outfit_name")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("outfit_name"),
                temp_table_name=sql.Identifier("tempo_outfit_name"),
                pk_name=sql.Identifier("outfit_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: transform_outfit.TransformOutfitName(lang_tag=self.lang_tag),
            "outfit": LoadOutfit(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }
