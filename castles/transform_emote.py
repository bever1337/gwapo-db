import enum
import luigi
from os import path

import common
import config
import extract_batch
import transform_csv


class EmoteTable(enum.Enum):
    Emote = "emote"
    EmoteCommand = "emote_command"
    EmoteItem = "emote_item"


class TransformEmote(transform_csv.TransformCsvTask):
    table = luigi.EnumParameter(enum=EmoteTable)

    def output(self):
        gwapo_config = config.gconfig()
        output_folder_name = "_".join(["transform", self.table.value])
        return common.from_output_params(
            output_dir=path.join(gwapo_config.output_dir, output_folder_name),
            extract_datetime=gwapo_config.extract_datetime,
            params={},
            ext="csv",
        )

    def requires(self):
        return extract_batch.ExtractBatchTask(
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
            case EmoteTable.EmoteItem:
                return [
                    {"emote_id": emote_id, "item_id": item_id}
                    for item_id in emote["unlock_items"]
                ]
            case _:
                raise RuntimeError("Unexpected table name")
