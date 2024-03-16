import luigi

import emote_extract
from tasks import config
from tasks import transform_csv


class TransformCsvEmoteTask(transform_csv.TransformCsvTask):
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "emote"

    def requires(self):
        return emote_extract.ExtractBatch()


class TransformCsvEmote(TransformCsvEmoteTask):
    def get_rows(self, emote):
        return [{"emote_id": emote["id"]}]


class TransformCsvEmoteCommand(TransformCsvEmoteTask):
    def get_rows(self, emote):
        return [
            {"command": command, "emote_id": emote["id"]} for command in ["commands"]
        ]


class TransformCsvEmoteItem(TransformCsvEmoteTask):
    def get_rows(self, emote):
        return [
            {"emote_id": emote["id"], "item_id": item_id}
            for item_id in emote["unlock_items"]
        ]
