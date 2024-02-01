import datetime
import enum
import luigi
from os import path

import common
import extract_batch
import transform_csv


class EmoteTable(enum.Enum):
    Emote = "emote"
    EmoteCommand = "emote_command"


class TransformEmote(transform_csv.TransformCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    output_dir = luigi.PathParameter(absolute=True, exists=True)
    table = luigi.EnumParameter(enum=EmoteTable)

    def output(self):
        output_folder_name = "_".join(["transform", self.table.value])
        return common.from_output_params(
            output_dir=path.join(self.output_dir, output_folder_name),
            extract_datetime=self.extract_datetime,
            params={},
            ext="csv",
        )

    def requires(self):
        return extract_batch.ExtractBatchTask(
            extract_datetime=self.extract_datetime,
            json_schema_path="./schema/gw2/v2/emotes/index.json",
            output_dir=self.output_dir,
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
