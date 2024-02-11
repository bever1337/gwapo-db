import datetime
import luigi
from psycopg import sql

import common
import load_csv
import load_lang
import transform_mount


class WrapMount(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadMount(**args)
        yield LoadMountName(**args)


class LoadMountTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)


class LoadMount(LoadMountTask):
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
        return {self.table: transform_mount.TransformMount(lang_tag=self.lang_tag)}


class LoadMountName(LoadMountTask):
    table = "mount_name"

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_mount_name")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("mount_name"),
                temp_table_name=sql.Identifier("tempo_mount_name"),
                pk_name=sql.Identifier("mount_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: transform_mount.TransformMountName(lang_tag=self.lang_tag),
            "mount": LoadMount(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }
