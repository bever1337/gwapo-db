import datetime
import luigi
from psycopg import sql

import common
from tasks import load_csv
import item_load_csv
import emote_transform_csv


class WrapEmote(luigi.WrapperTask):
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())

    def requires(self):
        args = {"task_datetime": self.task_datetime}
        yield LoadCsvEmote(**args)
        yield LoadCsvEmoteCommand(**args)


class LoadCsvEmoteTask(load_csv.LoadCsvTask):
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "emote"


class LoadCsvEmote(LoadCsvEmoteTask):
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
        return {self.table: emote_transform_csv.TransformCsvEmote()}


class LoadCsvEmoteCommand(LoadCsvEmoteTask):
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
            self.table: emote_transform_csv.TransformCsvEmoteCommand(),
            "emote": LoadCsvEmote(),
        }


class LoadCsvEmoteItem(LoadCsvEmoteTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    table = "emote_item"

    postcopy_sql = item_load_csv.merge_into_item_reference.format(
        cross_table_name=sql.Identifier("emote_item"),
        table_name=sql.Identifier("emote"),
        temp_table_name=sql.Identifier("tempo_emote_item"),
        pk_name=sql.Identifier("emote_id"),
    )

    def requires(self):
        return {
            self.table: emote_transform_csv.TransformCsvEmoteItem(),
            "emote": LoadCsvEmote(),
            "item": item_load_csv.LoadCsvItem(lang_tag=self.lang_tag),
        }
