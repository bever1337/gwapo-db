import datetime
import luigi
from os import path
from psycopg import sql

import common
import config
import load_csv
import transform_emote


class WrapEmote(luigi.WrapperTask):
    def requires(self):
        yield LoadEmote()
        yield LoadEmoteCommand()


class LoadEmoteTask(load_csv.LoadCsvTask):
    table = luigi.EnumParameter(enum=transform_emote.EmoteTable)

    def output(self):
        gwapo_config = config.gconfig()
        output_folder_name = "_".join(["load", self.table.value])
        return common.from_output_params(
            output_dir=path.join(gwapo_config.output_dir, output_folder_name),
            extract_datetime=gwapo_config.extract_datetime,
            params={},
            ext="txt",
        )


class LoadEmote(LoadEmoteTask):
    table = transform_emote.EmoteTable.Emote

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
        return {self.table.value: transform_emote.TransformEmote(table=self.table)}


class LoadEmoteCommand(LoadEmoteTask):
    table = transform_emote.EmoteTable.EmoteCommand

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
            self.table.value: transform_emote.TransformEmote(table=self.table),
            transform_emote.EmoteTable.Emote.value: LoadEmote(),
        }
