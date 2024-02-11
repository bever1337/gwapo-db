import extract_batch
import transform_csv


class TransformEmoteTask(transform_csv.TransformCsvTask):
    def requires(self):
        return extract_batch.ExtractBatchTask(
            json_schema_path="./schema/gw2/v2/emotes/index.json",
            url="https://api.guildwars2.com/v2/emotes",
        )


class TransformEmote(TransformEmoteTask):
    def get_rows(self, emote):
        return [{"emote_id": emote["id"]}]


class TransformEmoteCommand(TransformEmoteTask):
    def get_rows(self, emote):
        return [
            {"command": command, "emote_id": emote["id"]} for command in ["commands"]
        ]


class TransformEmoteItem(TransformEmoteTask):
    def get_rows(self, emote):
        return [
            {"emote_id": emote["id"], "item_id": item_id}
            for item_id in emote["unlock_items"]
        ]
