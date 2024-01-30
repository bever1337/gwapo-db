import datetime
import enum
import luigi
from os import path

import extract_batch
import load_csv


class EmoteTable(enum.Enum):
    Emote = "emote"
    EmoteCommand = "emote_command"


class TransformCurrency(load_csv.LoadCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    output_dir = luigi.PathParameter(absolute=True, exists=True)
    table = luigi.EnumParameter(enum=EmoteTable)

    def output(self):
        target_filename = "{timestamp:s}.csv".format(lang_tag=self.lang_tag.value)
        target_dir = "_".join(["transform", self.table.value])
        target_path = path.join(
            self.output_dir,
            target_dir,
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        return extract_batch.ExtractBatchTask(
            extract_datetime=self.extract_datetime,
            output_dir=self.output_dir,
            json_schema_path="./schema/gw2/v2/emotes/index.json",
            url="https://api.guildwars2.com/v2/emotes",
        )

    def get_rows(self, emote):
        emote_id = emote["id"]
        match self.table:
            case EmoteTable.Emote:
                return [{"emote_id": emote_id}]
            case EmoteTable.EmoteCommand:
                return [
                    {"command": command, "emote_id": emote_id}
                    for command in ["commands"]
                ]
            case _:
                raise RuntimeError("Unexpected table name")
