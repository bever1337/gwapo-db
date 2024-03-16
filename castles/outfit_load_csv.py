import luigi
from psycopg import sql

import common
import item_load_csv
import lang_load
import outfit_transform_csv
from tasks import config
from tasks import load_csv


class WrapOutfit(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvOutfit(**args)
        yield LoadCsvOutfitName(**args)


class LoadCsvOutfitTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "outfit"


class WrapOutfitTranslate(luigi.WrapperTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        for lang_tag in common.LangTag:
            if lang_tag == self.original_lang_tag:
                continue
            yield LoadCsvOutfitNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                task_datetime=self.task_datetime,
                translation_lang_tag=lang_tag,
            )


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


class LoadCsvOutfitName(lang_load.LangLoadCopySourceTask):
    id_attributes = [("outfit_id", sql.SQL("integer NOT NULL"))]
    table = "outfit_name"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "outfit"

    def requires(self):
        return {
            self.table: outfit_transform_csv.TransformCsvOutfitName(
                lang_tag=self.lang_tag
            ),
            "outfit": LoadCsvOutfit(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }


class LoadCsvOutfitNameTranslation(lang_load.LangLoadCopyTargetTask):
    id_attributes = [("outfit_id", sql.SQL("integer NOT NULL"))]
    table = "outfit_name_context"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "outfit"
    widget_table = "outfit_name"

    def requires(self):
        return {
            self.table: outfit_transform_csv.TransformCsvOutfitNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                translation_lang_tag=self.translation_lang_tag,
            ),
            "_": LoadCsvOutfitName(lang_tag=self.original_lang_tag),
        }
