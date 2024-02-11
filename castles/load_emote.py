import datetime
import luigi
from psycopg import sql

import common
import load_csv
import load_item
import transform_emote


class WrapEmote(luigi.WrapperTask):
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())

    def requires(self):
        args = {"task_datetime": self.task_datetime}
        yield LoadEmote(**args)
        yield LoadEmoteCommand(**args)


class LoadEmoteTask(load_csv.LoadCsvTask):
    pass


class LoadEmote(LoadEmoteTask):
    table = "emote"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.emote AS target_emote
USING tempo_emote AS source_emote ON target_emote.emote_id = source_emote.emote_id
WHEN NOT MATCHED THEN
  INSERT (emote_id)
    VALUES (source_emote.emote_id);
"""
    )

    def requires(self):
        return {self.table: transform_emote.TransformEmote()}


class LoadEmoteCommand(LoadEmoteTask):
    table = "emote_command"

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM gwapese.emote_command
WHERE NOT EXISTS (
    SELECT
    FROM
      tempo_emote_command
    WHERE
      gwapese.emote_command.command = tempo_emote_command.command
      AND gwapese.emote_command.emote_id = tempo_emote_command.emote_id);
"""
            ),
            sql.SQL(
                """
MERGE INTO gwapese.emote_command AS target_emote_command
USING tempo_emote_command AS source_emote_command ON
  target_emote_command.command = source_emote_command.command
  AND target_emote_command.emote_id = source_emote_command.emote_id
WHEN NOT MATCHED THEN
  INSERT (command, emote_id)
    VALUES (source_emote_command.command, source_emote_command.emote_id);
"""
            ),
        ]
    )

    def requires(self):
        return {
            self.table: transform_emote.TransformEmoteCommand(),
            "emote": LoadEmote(),
        }


class LoadEmoteItem(LoadEmoteTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    table = "emote_item"

    postcopy_sql = load_item.merge_into_item_reference.format(
        cross_table_name=sql.Identifier("emote_item"),
        table_name=sql.Identifier("emote"),
        temp_table_name=sql.Identifier("tempo_emote_item"),
        pk_name=sql.Identifier("emote_id"),
    )

    def requires(self):
        return {
            self.table: transform_emote.TransformEmoteItem(),
            "emote": LoadEmote(),
            "item": load_item.LoadItem(lang_tag=self.lang_tag),
        }
