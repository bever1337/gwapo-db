import datetime
import luigi
from os import path
from psycopg import sql

import common
import load_csv
import load_lang
import transform_novelty


class SeedNovelty(luigi.WrapperTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)

    def requires(self):
        args = {
            "extract_datetime": self.extract_datetime,
            "lang_tag": self.lang_tag,
            "output_dir": self.output_dir,
        }
        yield LoadNovelty(**args)
        yield LoadNoveltyDescription(**args)
        yield LoadNoveltyName(**args)


class LoadNoveltyTask(load_csv.LoadCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)
    table = luigi.EnumParameter(enum=transform_novelty.NoveltyTable)

    def output(self):
        output_folder_name = "_".join(["load", self.table.value])
        return common.from_output_params(
            output_dir=path.join(self.output_dir, output_folder_name),
            extract_datetime=self.extract_datetime,
            params={"lang": self.lang_tag.value},
            ext="txt",
        )


class LoadNovelty(LoadNoveltyTask):
    table = transform_novelty.NoveltyTable.Novelty

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
            self.table.value: transform_novelty.TransformNovelty(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
                table=self.table,
            )
        }


class LoadNoveltyDescription(LoadNoveltyTask):
    table = transform_novelty.NoveltyTable.NoveltyDescription

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_novelty_description")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("novelty_description"),
                temp_table_name=sql.Identifier("tempo_novelty_description"),
                pk_name=sql.Identifier("novelty_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table.value: transform_novelty.TransformNovelty(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
                table=self.table,
            ),
            transform_novelty.NoveltyTable.Novelty.value: LoadNovelty(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
            ),
            "lang": load_lang.LoadLang(
                extract_datetime=self.extract_datetime, output_dir=self.output_dir
            ),
        }


class LoadNoveltyName(LoadNoveltyTask):
    table = transform_novelty.NoveltyTable.NoveltyName

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_novelty_name")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("novelty_name"),
                temp_table_name=sql.Identifier("tempo_novelty_name"),
                pk_name=sql.Identifier("novelty_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table.value: transform_novelty.TransformNovelty(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
                table=self.table,
            ),
            transform_novelty.NoveltyTable.Novelty.value: LoadNovelty(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
            ),
            "lang": load_lang.LoadLang(
                extract_datetime=self.extract_datetime, output_dir=self.output_dir
            ),
        }
