import luigi
from os import path
from psycopg import sql

import common
import config
import load_csv
import load_lang
import transform_novelty


class WrapNovelty(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        args = {"lang_tag": self.lang_tag}
        yield LoadNovelty(**args)
        yield LoadNoveltyDescription(**args)
        yield LoadNoveltyName(**args)


class LoadNoveltyTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    table = luigi.EnumParameter(enum=transform_novelty.NoveltyTable)

    def output(self):
        gwapo_config = config.gconfig()
        output_folder_name = "_".join(["load", self.table.value])
        return common.from_output_params(
            output_dir=path.join(gwapo_config.output_dir, output_folder_name),
            extract_datetime=gwapo_config.extract_datetime,
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
                lang_tag=self.lang_tag, table=self.table
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
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_novelty.NoveltyTable.Novelty.value: LoadNovelty(
                lang_tag=self.lang_tag
            ),
            "lang": load_lang.LoadLang(),
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
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_novelty.NoveltyTable.Novelty.value: LoadNovelty(
                lang_tag=self.lang_tag
            ),
            "lang": load_lang.LoadLang(),
        }
