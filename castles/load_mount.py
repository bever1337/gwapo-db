import datetime
import luigi
from os import path
from psycopg import sql

import common
import load_csv
import load_lang
import transform_mount


class SeedMount(luigi.WrapperTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)

    def requires(self):
        args = {
            "extract_datetime": self.extract_datetime,
            "lang_tag": self.lang_tag,
            "output_dir": self.output_dir,
        }
        yield LoadMount(**args)
        yield LoadMountName(**args)


class LoadMountTask(load_csv.LoadCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)
    table = luigi.EnumParameter(enum=transform_mount.MountTable)

    def output(self):
        output_folder_name = "_".join(["load", self.table.value])
        return common.from_output_params(
            output_dir=path.join(self.output_dir, output_folder_name),
            extract_datetime=self.extract_datetime,
            params={"lang": self.lang_tag.value},
            ext="txt",
        )


class LoadMount(LoadMountTask):
    table = transform_mount.MountTable.Mount

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
            self.table.value: transform_mount.TransformMount(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
                table=self.table,
            )
        }


class LoadMountName(LoadMountTask):
    table = transform_mount.MountTable.MountName

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
            self.table.value: transform_mount.TransformMount(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
                table=self.table,
            ),
            transform_mount.MountTable.Mount.value: LoadMount(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
            ),
            "lang": load_lang.LoadLang(
                extract_datetime=self.extract_datetime, output_dir=self.output_dir
            ),
        }
