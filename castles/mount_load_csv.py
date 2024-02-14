import datetime
import luigi
from psycopg import sql

import common
from tasks import load_csv
import lang_load
import mount_transform_csv


class WrapMount(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvMount(**args)
        yield LoadCsvMountName(**args)


class LoadCsvMountTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
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


class LoadCsvMountName(LoadCsvMountTask):
    table = "mount_name"

    postcopy_sql = sql.Composed(
        [
            lang_load.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_mount_name")
            ),
            lang_load.merge_into_placed_copy.format(
                table_name=sql.Identifier("mount_name"),
                temp_table_name=sql.Identifier("tempo_mount_name"),
                pk_name=sql.Identifier("mount_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: mount_transform_csv.TransformCsvMountName(
                lang_tag=self.lang_tag
            ),
            "mount": LoadCsvMount(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }
