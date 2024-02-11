import datetime
import luigi
from psycopg import sql

import common
import load_csv
import load_item
import load_lang
import transform_jade_bot


class WrapJadeBot(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadJadeBot(**args)
        yield LoadJadeBotDescription(**args)
        yield LoadJadeBotName(**args)


class LoadJadeBotTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)


class LoadJadeBot(LoadJadeBotTask):
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
        return {self.table: transform_jade_bot.TransformJadeBot(lang_tag=self.lang_tag)}


class LoadJadeBotDescription(LoadJadeBotTask):
    table = "jade_bot_description"

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_jade_bot_description")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("jade_bot_description"),
                temp_table_name=sql.Identifier("tempo_jade_bot_description"),
                pk_name=sql.Identifier("jade_bot_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: transform_jade_bot.TransformJadeBotDescription(
                lang_tag=self.lang_tag
            ),
            "jade_bot": LoadJadeBot(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }


class LoadJadeBotItem(LoadJadeBotTask):
    table = "jade_bot_item"

    postcopy_sql = load_item.merge_into_item_reference.format(
        cross_table_name=sql.Identifier("jade_bot_item"),
        table_name=sql.Identifier("jade_bot"),
        temp_table_name=sql.Identifier("tempo_jade_bot_item"),
        pk_name=sql.Identifier("jade_bot_id"),
    )

    def requires(self):
        return {
            self.table: transform_jade_bot.TransformJadeBotItem(lang_tag=self.lang_tag),
            "jade_bot": LoadJadeBot(lang_tag=self.lang_tag),
            "item": load_item.LoadItem(lang_tag=self.lang_tag),
        }


class LoadJadeBotName(LoadJadeBotTask):
    table = "jade_bot_name"

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_jade_bot_name")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("jade_bot_name"),
                temp_table_name=sql.Identifier("tempo_jade_bot_name"),
                pk_name=sql.Identifier("jade_bot_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: transform_jade_bot.TransformJadeBotName(lang_tag=self.lang_tag),
            "jade_bot": LoadJadeBot(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }
