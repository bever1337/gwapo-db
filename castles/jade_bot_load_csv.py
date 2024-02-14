import datetime
import luigi
from psycopg import sql

import common
from tasks import load_csv
import item_load_csv
import lang_load
import jade_bot_transform_csv


class WrapJadeBot(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvJadeBot(**args)
        yield LoadCsvJadeBotDescription(**args)
        yield LoadCsvJadeBotName(**args)


class LoadCsvJadeBotTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "jade_bot"


class LoadCsvJadeBot(LoadCsvJadeBotTask):
    table = "jade_bot"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.jade_bot AS target_jade_bot
USING tempo_jade_bot AS source_jade_bot ON target_jade_bot.jade_bot_id =
  source_jade_bot.jade_bot_id
WHEN NOT MATCHED THEN
  INSERT (jade_bot_id)
    VALUES (source_jade_bot.jade_bot_id);
"""
    )

    def requires(self):
        return {
            self.table: jade_bot_transform_csv.TransformCsvJadeBot(
                lang_tag=self.lang_tag
            )
        }


class LoadCsvJadeBotDescription(LoadCsvJadeBotTask):
    table = "jade_bot_description"

    postcopy_sql = sql.Composed(
        [
            lang_load.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_jade_bot_description")
            ),
            lang_load.merge_into_placed_copy.format(
                table_name=sql.Identifier("jade_bot_description"),
                temp_table_name=sql.Identifier("tempo_jade_bot_description"),
                pk_name=sql.Identifier("jade_bot_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: jade_bot_transform_csv.TransformCsvJadeBotDescription(
                lang_tag=self.lang_tag
            ),
            "jade_bot": LoadCsvJadeBot(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }


class LoadCsvJadeBotItem(LoadCsvJadeBotTask):
    table = "jade_bot_item"

    postcopy_sql = item_load_csv.merge_into_item_reference.format(
        cross_table_name=sql.Identifier("jade_bot_item"),
        table_name=sql.Identifier("jade_bot"),
        temp_table_name=sql.Identifier("tempo_jade_bot_item"),
        pk_name=sql.Identifier("jade_bot_id"),
    )

    def requires(self):
        return {
            self.table: jade_bot_transform_csv.TransformCsvJadeBotItem(
                lang_tag=self.lang_tag
            ),
            "jade_bot": LoadCsvJadeBot(lang_tag=self.lang_tag),
            "item": item_load_csv.LoadCsvItem(lang_tag=self.lang_tag),
        }


class LoadCsvJadeBotName(LoadCsvJadeBotTask):
    table = "jade_bot_name"

    postcopy_sql = sql.Composed(
        [
            lang_load.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_jade_bot_name")
            ),
            lang_load.merge_into_placed_copy.format(
                table_name=sql.Identifier("jade_bot_name"),
                temp_table_name=sql.Identifier("tempo_jade_bot_name"),
                pk_name=sql.Identifier("jade_bot_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: jade_bot_transform_csv.TransformCsvJadeBotName(
                lang_tag=self.lang_tag
            ),
            "jade_bot": LoadCsvJadeBot(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }
