import datetime
import luigi
from psycopg import sql

import common
import load_csv
import load_item
import load_lang
import transform_finisher


class WrapFinisher(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_dateime": self.task_datetime}
        yield LoadFinisher(**args)
        yield LoadFinisherDetail(**args)
        yield LoadFinisherName(**args)


class LoadFinisherTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)


class LoadFinisher(LoadFinisherTask):
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
            self.table: transform_finisher.TransformFinisher(lang_tag=self.lang_tag)
        }


class LoadFinisherDetail(LoadFinisherTask):
    table = "finisher_detail"

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_finisher_detail")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("finisher_detail"),
                temp_table_name=sql.Identifier("tempo_finisher_detail"),
                pk_name=sql.Identifier("finisher_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: transform_finisher.TransformFinisherDetail(
                lang_tag=self.lang_tag
            ),
            "finisher": LoadFinisher(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }


class LoadFinisherItem(LoadFinisherTask):
    table = "finisher_item"

    postcopy_sql = load_item.merge_into_item_reference.format(
        cross_table_name=sql.Identifier("finisher_item"),
        table_name=sql.Identifier("finisher"),
        temp_table_name=sql.Identifier("tempo_finisher_item"),
        pk_name=sql.Identifier("finisher_id"),
    )

    def requires(self):
        return {
            self.table: transform_finisher.TransformFinisherItem(
                lang_tag=self.lang_tag
            ),
            "finisher": LoadFinisher(lang_tag=self.lang_tag),
            "item": load_item.LoadItem(lang_tag=self.lang_tag),
        }


class LoadFinisherName(LoadFinisherTask):
    table = "finisher_name"

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_finisher_name")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("finisher_name"),
                temp_table_name=sql.Identifier("tempo_finisher_name"),
                pk_name=sql.Identifier("finisher_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: transform_finisher.TransformFinisherName(
                lang_tag=self.lang_tag
            ),
            "finisher": LoadFinisher(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }
