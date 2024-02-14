import datetime
import luigi
from psycopg import sql

import common
from tasks import load_csv
import item_load_csv
import lang_load
import outfit_transform_csv


class WrapOutfit(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvOutfit(**args)
        yield LoadCsvOutfitName(**args)


class LoadCsvOutfitTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "outfit"


class LoadCsvOutfit(LoadCsvOutfitTask):
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
        return {
            self.table: outfit_transform_csv.TransformCsvOutfit(lang_tag=self.lang_tag)
        }


class LoadCsvOutfitItem(LoadCsvOutfitTask):
    table = "outfit_item"

    postcopy_sql = item_load_csv.merge_into_item_reference.format(
        cross_table_name=sql.Identifier("outfit_item"),
        table_name=sql.Identifier("outfit"),
        temp_table_name=sql.Identifier("tempo_outfit_item"),
        pk_name=sql.Identifier("outfit_id"),
    )

    def requires(self):
        return {
            self.table: outfit_transform_csv.TransformCsvOutfitItem(
                lang_tag=self.lang_tag
            ),
            "outfit": LoadCsvOutfit(lang_tag=self.lang_tag),
            "item": item_load_csv.LoadCsvItem(lang_tag=self.lang_tag),
        }


class LoadCsvOutfitName(LoadCsvOutfitTask):
    table = "outfit_name"

    postcopy_sql = sql.Composed(
        [
            lang_load.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_outfit_name")
            ),
            lang_load.merge_into_placed_copy.format(
                table_name=sql.Identifier("outfit_name"),
                temp_table_name=sql.Identifier("tempo_outfit_name"),
                pk_name=sql.Identifier("outfit_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: outfit_transform_csv.TransformCsvOutfitName(
                lang_tag=self.lang_tag
            ),
            "outfit": LoadCsvOutfit(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }
