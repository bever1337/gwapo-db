import datetime
import luigi
from psycopg import sql

import common
from tasks import load_csv
import item_load_csv
import lang_load
import mini_transform_csv


class WrapMini(luigi.WrapperTask):
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvMini(**args)
        yield LoadCsvMiniName(**args)
        yield LoadCsvMiniUnlock(**args)


class LoadCsvMiniTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "mini"


class LoadCsvMini(LoadCsvMiniTask):
    table = "mini"

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
        return {self.table: mini_transform_csv.TransformCsvMini(lang_tag=self.lang_tag)}


class LoadCsvMiniItem(LoadCsvMiniTask):
    table = "mini_item"

    postcopy_sql = item_load_csv.merge_into_item_reference.format(
        cross_table_name=sql.Identifier("mini_item"),
        table_name=sql.Identifier("mini"),
        temp_table_name=sql.Identifier("tempo_mini_item"),
        pk_name=sql.Identifier("mini_id"),
    )

    def requires(self):
        return {
            self.table: mini_transform_csv.TransformCsvMiniItem(lang_tag=self.lang_tag),
            "mini": LoadCsvMini(lang_tag=self.lang_tag),
            "item": item_load_csv.LoadCsvItem(lang_tag=self.lang_tag),
        }


class LoadCsvMiniName(LoadCsvMiniTask):
    table = "mini_name"

    postcopy_sql = sql.Composed(
        [
            lang_load.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_mini_name")
            ),
            lang_load.merge_into_placed_copy.format(
                table_name=sql.Identifier("mini_name"),
                temp_table_name=sql.Identifier("tempo_mini_name"),
                pk_name=sql.Identifier("mini_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: mini_transform_csv.TransformCsvMiniName(lang_tag=self.lang_tag),
            "mini": LoadCsvMini(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }


class LoadCsvMiniUnlock(LoadCsvMiniTask):
    table = "mini_unlock"

    postcopy_sql = sql.Composed(
        [
            lang_load.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_mini_unlock")
            ),
            lang_load.merge_into_placed_copy.format(
                table_name=sql.Identifier("mini_unlock"),
                temp_table_name=sql.Identifier("tempo_mini_unlock"),
                pk_name=sql.Identifier("mini_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: mini_transform_csv.TransformCsvMiniUnlock(
                lang_tag=self.lang_tag
            ),
            "mini": LoadCsvMini(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }
