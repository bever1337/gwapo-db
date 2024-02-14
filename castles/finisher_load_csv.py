import datetime
import luigi
from psycopg import sql

import common
from tasks import load_csv
import item_load_csv
import lang_load
import finisher_transform_csv


class WrapFinisher(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvFinisher(**args)
        yield LoadCsvFinisherDetail(**args)
        yield LoadCsvFinisherName(**args)


class LoadCsvFinisherTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
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


class LoadCsvFinisherDetail(LoadCsvFinisherTask):
    table = "finisher_detail"

    postcopy_sql = sql.Composed(
        [
            lang_load.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_finisher_detail")
            ),
            lang_load.merge_into_placed_copy.format(
                table_name=sql.Identifier("finisher_detail"),
                temp_table_name=sql.Identifier("tempo_finisher_detail"),
                pk_name=sql.Identifier("finisher_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: finisher_transform_csv.TransformCsvFinisherDetail(
                lang_tag=self.lang_tag
            ),
            "finisher": LoadCsvFinisher(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
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


class LoadCsvFinisherName(LoadCsvFinisherTask):
    table = "finisher_name"

    postcopy_sql = sql.Composed(
        [
            lang_load.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_finisher_name")
            ),
            lang_load.merge_into_placed_copy.format(
                table_name=sql.Identifier("finisher_name"),
                temp_table_name=sql.Identifier("tempo_finisher_name"),
                pk_name=sql.Identifier("finisher_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: finisher_transform_csv.TransformCsvFinisherName(
                lang_tag=self.lang_tag
            ),
            "finisher": LoadCsvFinisher(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }
