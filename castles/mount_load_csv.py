import luigi
from psycopg import sql

import common
import lang_load
import mount_transform_csv
from tasks import config
from tasks import load_csv


class WrapMount(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvMount(**args)
        yield LoadCsvMountName(**args)


class WrapMountTranslate(luigi.WrapperTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        for lang_tag in common.LangTag:
            if lang_tag == self.original_lang_tag:
                continue
            yield LoadCsvMountNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                task_datetime=self.task_datetime,
                translation_lang_tag=lang_tag,
            )


class LoadCsvMountTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "mount"


class LoadCsvMount(LoadCsvMountTask):
    table = "mount"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.mount AS target_mount
USING tempo_mount AS source_mount ON target_mount.mount_id = source_mount.mount_id
WHEN NOT MATCHED THEN
  INSERT (mount_id)
    VALUES (source_mount.mount_id);
"""
    )

    def requires(self):
        return {
            self.table: mount_transform_csv.TransformCsvMount(lang_tag=self.lang_tag)
        }


class LoadCsvMountName(lang_load.LangLoadCopySourceTask):
    id_attributes = [("mount_id", sql.SQL("text NOT NULL"))]
    table = "mount_name"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "mount"

    def requires(self):
        return {
            self.table: mount_transform_csv.TransformCsvMountName(
                lang_tag=self.lang_tag
            ),
            "mount": LoadCsvMount(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }


class LoadCsvMountNameTranslation(lang_load.LangLoadCopyTargetTask):
    id_attributes = [("mount_id", sql.SQL("text NOT NULL"))]
    table = "mount_name_context"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "mount"
    widget_table = "mount_name"

    def requires(self):
        return {
            self.table: mount_transform_csv.TransformCsvMountNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                translation_lang_tag=self.translation_lang_tag,
            ),
            "_": LoadCsvMountName(lang_tag=self.original_lang_tag),
        }
