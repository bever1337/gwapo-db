import datetime
import luigi
from os import path
from psycopg import sql

import common
import load_csv
import load_lang
import transform_jade_bot


class LoadJadeBotTask(load_csv.LoadCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)
    table = luigi.EnumParameter(enum=transform_jade_bot.JadeBotTable)

    def output(self):
        output_folder_name = "_".join(["load", self.table.value])
        return common.from_output_params(
            output_dir=path.join(self.output_dir, output_folder_name),
            extract_datetime=self.extract_datetime,
            params={"lang": self.lang_tag.value},
            ext="txt",
        )

    def requires(self):
        return transform_jade_bot.TransformJadeBot(
            extract_datetime=self.extract_datetime,
            lang_tag=self.lang_tag,
            output_dir=self.output_dir,
            table=self.table,
        )


class LoadJadeBot(LoadJadeBotTask):
    table = transform_jade_bot.JadeBotTable.JadeBot

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.jade_bot AS target_jade_bot
USING tempo_jade_bot AS source_jade_bot
ON target_jade_bot.jade_bot_id = source_jade_bot.jade_bot_id
WHEN NOT MATCHED THEN
  INSERT (jade_bot_id) VALUES (source_jade_bot.jade_bot_id);
"""
    )


class LoadJadeBotDescription(LoadJadeBotTask):
    table = transform_jade_bot.JadeBotTable.JadeBotDescription

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


class LoadJadeBotName(LoadJadeBotTask):
    table = transform_jade_bot.JadeBotTable.JadeBotName

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
