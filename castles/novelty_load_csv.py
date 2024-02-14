import datetime
import luigi
from psycopg import sql

import common
from tasks import load_csv
import item_load_csv
import lang_load
import novelty_transform_csv


class WrapNovelty(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvNovelty(**args)
        yield LoadCsvNoveltyDescription(**args)
        yield LoadCsvNoveltyName(**args)


class LoadCsvNoveltyTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
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


class LoadCsvNoveltyDescription(LoadCsvNoveltyTask):
    table = "novelty_description"

    postcopy_sql = sql.Composed(
        [
            lang_load.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_novelty_description")
            ),
            lang_load.merge_into_placed_copy.format(
                table_name=sql.Identifier("novelty_description"),
                temp_table_name=sql.Identifier("tempo_novelty_description"),
                pk_name=sql.Identifier("novelty_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: novelty_transform_csv.TransformCsvNoveltyDescription(
                lang_tag=self.lang_tag
            ),
            "novelty": LoadCsvNovelty(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
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


class LoadCsvNoveltyName(LoadCsvNoveltyTask):
    table = "novelty_name"

    postcopy_sql = sql.Composed(
        [
            lang_load.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_novelty_name")
            ),
            lang_load.merge_into_placed_copy.format(
                table_name=sql.Identifier("novelty_name"),
                temp_table_name=sql.Identifier("tempo_novelty_name"),
                pk_name=sql.Identifier("novelty_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: novelty_transform_csv.TransformCsvNoveltyName(
                lang_tag=self.lang_tag
            ),
            "novelty": LoadCsvNovelty(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }
