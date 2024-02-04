import datetime
import luigi
from os import path
from psycopg import sql

import common
import load_csv
import load_lang
import transform_mini


class SeedMini(luigi.WrapperTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)

    def requires(self):
        args = {
            "extract_datetime": self.extract_datetime,
            "lang_tag": self.lang_tag,
            "output_dir": self.output_dir,
        }
        yield LoadMini(**args)
        yield LoadMiniName(**args)
        yield LoadMiniUnlock(**args)


class LoadMiniTask(load_csv.LoadCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)
    table = luigi.EnumParameter(enum=transform_mini.MiniTable)

    def output(self):
        output_folder_name = "_".join(["load", self.table.value])
        return common.from_output_params(
            output_dir=path.join(self.output_dir, output_folder_name),
            extract_datetime=self.extract_datetime,
            params={"lang": self.lang_tag.value},
            ext="txt",
        )


class LoadMini(LoadMiniTask):
    table = transform_mini.MiniTable.Mini

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
        return {
            self.table.value: transform_mini.TransformMini(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
                table=self.table,
            )
        }


class LoadMiniName(LoadMiniTask):
    table = transform_mini.MiniTable.MiniName

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_mini_name")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("mini_name"),
                temp_table_name=sql.Identifier("tempo_mini_name"),
                pk_name=sql.Identifier("mini_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table.value: transform_mini.TransformMini(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
                table=self.table,
            ),
            transform_mini.MiniTable.Mini.value: LoadMini(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
            ),
            "lang": load_lang.LoadLang(
                extract_datetime=self.extract_datetime, output_dir=self.output_dir
            ),
        }


class LoadMiniUnlock(LoadMiniTask):
    table = transform_mini.MiniTable.MiniUnlock

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_mini_unlock")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("mini_unlock"),
                temp_table_name=sql.Identifier("tempo_mini_unlock"),
                pk_name=sql.Identifier("mini_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table.value: transform_mini.TransformMini(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
                table=self.table,
            ),
            transform_mini.MiniTable.Mini.value: LoadMini(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
            ),
            "lang": load_lang.LoadLang(
                extract_datetime=self.extract_datetime, output_dir=self.output_dir
            ),
        }
