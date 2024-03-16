import luigi
from psycopg import sql

import common
import finisher_transform_csv
import item_load_csv
import lang_load
from tasks import config
from tasks import load_csv


class WrapFinisher(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvFinisher(**args)
        yield LoadCsvFinisherDetail(**args)
        yield LoadCsvFinisherName(**args)


class WrapFinisherTranslate(luigi.WrapperTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        for lang_tag in common.LangTag:
            if lang_tag == self.original_lang_tag:
                continue
            yield LoadCsvFinisherDetailTranslation(
                original_lang_tag=self.original_lang_tag,
                task_datetime=self.task_datetime,
                translation_lang_tag=lang_tag,
            )
            yield LoadCsvFinisherNameTranslation(
                original_lang_tag=self.original_lang_tag,
                task_datetime=self.task_datetime,
                translation_lang_tag=lang_tag,
            )


class LoadCsvFinisherTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "finisher"


class LoadCsvFinisher(LoadCsvFinisherTask):
    table = "finisher"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.finisher AS target_finisher
USING tempo_finisher AS source_finisher ON target_finisher.finisher_id =
  source_finisher.finisher_id
WHEN MATCHED
  AND target_finisher.icon != source_finisher.icon
  OR target_finisher.presentation_order != source_finisher.presentation_order THEN
  UPDATE SET
    (icon, presentation_order) = (source_finisher.icon, source_finisher.presentation_order)
WHEN NOT MATCHED THEN
  INSERT (finisher_id, icon, presentation_order)
    VALUES (source_finisher.finisher_id, source_finisher.icon,
      source_finisher.presentation_order);
"""
    )

    def requires(self):
        return {
            self.table: finisher_transform_csv.TransformCsvFinisher(
                lang_tag=self.lang_tag
            )
        }


class LoadCsvFinisherDetail(lang_load.LangLoadCopySourceTask):
    id_attributes = [("finisher_id", sql.SQL("integer NOT NULL"))]
    table = "finisher_detail"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "finisher"

    def requires(self):
        return {
            self.table: finisher_transform_csv.TransformCsvFinisherDetail(
                lang_tag=self.lang_tag
            ),
            "finisher": LoadCsvFinisher(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }


class LoadCsvFinisherDetailTranslation(lang_load.LangLoadCopyTargetTask):
    id_attributes = [("finisher_id", sql.SQL("integer NOT NULL"))]
    table = "finisher_detail_context"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "finisher"
    widget_table = "finisher_detail"

    def requires(self):
        return {
            self.table: finisher_transform_csv.TransformCsvFinisherDetailTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                translation_lang_tag=self.translation_lang_tag,
            ),
            "finisher": LoadCsvFinisherDetail(lang_tag=self.original_lang_tag),
        }


class LoadCsvFinisherItem(LoadCsvFinisherTask):
    table = "finisher_item"

    postcopy_sql = item_load_csv.merge_into_item_reference.format(
        cross_table_name=sql.Identifier("finisher_item"),
        table_name=sql.Identifier("finisher"),
        temp_table_name=sql.Identifier("tempo_finisher_item"),
        pk_name=sql.Identifier("finisher_id"),
    )

    def requires(self):
        return {
            self.table: finisher_transform_csv.TransformCsvFinisherItem(
                lang_tag=self.lang_tag
            ),
            "finisher": LoadCsvFinisher(lang_tag=self.lang_tag),
            "item": item_load_csv.LoadCsvItem(lang_tag=self.lang_tag),
        }


class LoadCsvFinisherName(lang_load.LangLoadCopySourceTask):
    id_attributes = [("finisher_id", sql.SQL("integer NOT NULL"))]
    table = "finisher_name"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "finisher"

    def requires(self):
        return {
            self.table: finisher_transform_csv.TransformCsvFinisherName(
                lang_tag=self.lang_tag
            ),
            "finisher": LoadCsvFinisher(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }


class LoadCsvFinisherNameTranslation(lang_load.LangLoadCopyTargetTask):
    id_attributes = [("finisher_id", sql.SQL("integer NOT NULL"))]
    table = "finisher_name_context"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "finisher"
    widget_table = "finisher_name"

    def requires(self):
        return {
            self.table: finisher_transform_csv.TransformCsvFinisherNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                translation_lang_tag=self.translation_lang_tag,
            ),
            "finisher": LoadCsvFinisherName(lang_tag=self.original_lang_tag),
        }
