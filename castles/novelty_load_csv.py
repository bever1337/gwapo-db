import luigi
from psycopg import sql

import common
import item_load_csv
import lang_load
import novelty_transform_csv
from tasks import config
from tasks import load_csv


class WrapNovelty(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvNovelty(**args)
        yield LoadCsvNoveltyDescription(**args)
        yield LoadCsvNoveltyName(**args)


class WrapNoveltyTranslate(luigi.WrapperTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        for lang_tag in common.LangTag:
            if lang_tag == self.original_lang_tag:
                continue
            yield LoadCsvNoveltyDescriptionTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                task_datetime=self.task_datetime,
                translation_lang_tag=lang_tag,
            )
            yield LoadCsvNoveltyNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                task_datetime=self.task_datetime,
                translation_lang_tag=lang_tag,
            )


class LoadCsvNoveltyTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "novelty"


class LoadCsvNovelty(LoadCsvNoveltyTask):
    table = "novelty"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.novelty AS target_novelty
USING tempo_novelty AS source_novelty ON target_novelty.novelty_id =
  source_novelty.novelty_id
WHEN MATCHED
  AND target_novelty.icon != source_novelty.icon
  OR target_novelty.slot != source_novelty.slot THEN
  UPDATE SET
    (icon, slot) = (source_novelty.icon, source_novelty.slot)
WHEN NOT MATCHED THEN
  INSERT (icon, novelty_id, slot)
    VALUES (source_novelty.icon, source_novelty.novelty_id, source_novelty.slot);
"""
    )

    def requires(self):
        return {
            self.table: novelty_transform_csv.TransformCsvNovelty(
                lang_tag=self.lang_tag
            )
        }


class LoadCsvNoveltyDescription(lang_load.LangLoadCopySourceTask):
    id_attributes = [("novelty_id", sql.SQL("integer NOT NULL"))]
    table = "novelty_description"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "novelty"

    def requires(self):
        return {
            self.table: novelty_transform_csv.TransformCsvNoveltyDescription(
                lang_tag=self.lang_tag
            ),
            "novelty": LoadCsvNovelty(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }


class LoadCsvNoveltyDescriptionTranslation(lang_load.LangLoadCopyTargetTask):
    id_attributes = [("novelty_id", sql.SQL("integer NOT NULL"))]
    table = "novelty_description_context"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "novelty"
    widget_table = "novelty_description"

    def requires(self):
        return {
            self.table: novelty_transform_csv.TransformCsvNoveltyDescriptionTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                translation_lang_tag=self.translation_lang_tag,
            ),
            "_": LoadCsvNoveltyDescription(lang_tag=self.original_lang_tag),
        }


class LoadCsvNoveltyItem(LoadCsvNoveltyTask):
    table = "novelty_item"

    postcopy_sql = item_load_csv.merge_into_item_reference.format(
        cross_table_name=sql.Identifier("novelty_item"),
        table_name=sql.Identifier("novelty"),
        temp_table_name=sql.Identifier("tempo_novelty_item"),
        pk_name=sql.Identifier("novelty_id"),
    )

    def requires(self):
        return {
            self.table: novelty_transform_csv.TransformCsvNoveltyItem(
                lang_tag=self.lang_tag
            ),
            "novelty": LoadCsvNovelty(lang_tag=self.lang_tag),
            "item": item_load_csv.LoadCsvItem(lang_tag=self.lang_tag),
        }


class LoadCsvNoveltyName(lang_load.LangLoadCopySourceTask):
    id_attributes = [("novelty_id", sql.SQL("integer NOT NULL"))]
    table = "novelty_name"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "novelty"

    def requires(self):
        return {
            self.table: novelty_transform_csv.TransformCsvNoveltyName(
                lang_tag=self.lang_tag
            ),
            "novelty": LoadCsvNovelty(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }


class LoadCsvNoveltyNameTranslation(lang_load.LangLoadCopyTargetTask):
    id_attributes = [("novelty_id", sql.SQL("integer NOT NULL"))]
    table = "novelty_name_context"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "novelty"
    widget_table = "novelty_name"

    def requires(self):
        return {
            self.table: novelty_transform_csv.TransformCsvNoveltyNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                translation_lang_tag=self.translation_lang_tag,
            ),
            "_": LoadCsvNoveltyName(lang_tag=self.original_lang_tag),
        }
