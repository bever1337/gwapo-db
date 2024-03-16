import luigi
from psycopg import sql

import common
import item_load_csv
import lang_load
import mini_transform_csv
from tasks import config
from tasks import load_csv


class WrapMini(luigi.WrapperTask):
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvMini(**args)
        yield LoadCsvMiniName(**args)
        yield LoadCsvMiniUnlock(**args)


class WrapMiniTranslate(luigi.WrapperTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        for lang_tag in common.LangTag:
            if lang_tag == self.original_lang_tag:
                continue
            yield LoadCsvMiniNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                task_datetime=self.task_datetime,
                translation_lang_tag=lang_tag,
            )
            yield LoadCsvMiniUnlockTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                task_datetime=self.task_datetime,
                translation_lang_tag=lang_tag,
            )


class LoadCsvMiniTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "mini"


class LoadCsvMini(LoadCsvMiniTask):
    table = "mini"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.mini AS target_mini
USING tempo_mini AS source_mini ON target_mini.mini_id = source_mini.mini_id
WHEN MATCHED
  AND target_mini.icon != source_mini.icon
  OR target_mini.presentation_order != source_mini.presentation_order THEN
  UPDATE SET
    (icon, presentation_order) = (source_mini.icon, source_mini.presentation_order)
WHEN NOT MATCHED THEN
  INSERT (icon, mini_id, presentation_order)
    VALUES (source_mini.icon, source_mini.mini_id, source_mini.presentation_order);
"""
    )

    def requires(self):
        return {self.table: mini_transform_csv.TransformCsvMini(lang_tag=self.lang_tag)}


class LoadCsvMiniItem(LoadCsvMiniTask):
    table = "mini_item"

    postcopy_sql = item_load_csv.merge_into_item_reference.format(
        cross_table_name=sql.Identifier("mini_item"),
        table_name=sql.Identifier("mini"),
        temp_table_name=sql.Identifier("tempo_mini_item"),
        pk_name=sql.Identifier("mini_id"),
    )

    def requires(self):
        return {
            self.table: mini_transform_csv.TransformCsvMiniItem(lang_tag=self.lang_tag),
            "mini": LoadCsvMini(lang_tag=self.lang_tag),
            "item": item_load_csv.LoadCsvItem(lang_tag=self.lang_tag),
        }


class LoadCsvMiniName(lang_load.LangLoadCopySourceTask):
    id_attributes = [("mini_id", sql.SQL("integer NOT NULL"))]
    table = "mini_name"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "mini"

    def requires(self):
        return {
            self.table: mini_transform_csv.TransformCsvMiniName(lang_tag=self.lang_tag),
            "mini": LoadCsvMini(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }


class LoadCsvMiniNameTranslation(lang_load.LangLoadCopyTargetTask):
    id_attributes = [("mini_id", sql.SQL("integer NOT NULL"))]
    table = "mini_name_context"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "mini"
    widget_table = "mini_name"

    def requires(self):
        return {
            self.table: mini_transform_csv.TransformCsvMiniNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                translation_lang_tag=self.translation_lang_tag,
            ),
            "_": LoadCsvMiniName(lang_tag=self.original_lang_tag),
        }


class LoadCsvMiniUnlock(lang_load.LangLoadCopySourceTask):
    id_attributes = [("mini_id", sql.SQL("integer NOT NULL"))]
    table = "mini_unlock"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "mini"

    def requires(self):
        return {
            self.table: mini_transform_csv.TransformCsvMiniUnlock(
                lang_tag=self.lang_tag
            ),
            "mini": LoadCsvMini(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }


class LoadCsvMiniUnlockTranslation(lang_load.LangLoadCopyTargetTask):
    id_attributes = [("mini_id", sql.SQL("integer NOT NULL"))]
    table = "mini_unlock_context"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "mini"
    widget_table = "mini_unlock"

    def requires(self):
        return {
            self.table: mini_transform_csv.TransformCsvMiniUnlockTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                translation_lang_tag=self.translation_lang_tag,
            ),
            "_": LoadCsvMiniUnlock(lang_tag=self.original_lang_tag),
        }
