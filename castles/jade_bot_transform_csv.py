import datetime
import luigi

import common
import jade_bot_extract
from tasks import transform_csv


class TransformCsvJadeBotTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "jade_bot"

    def requires(self):
        return jade_bot_extract.ExtractBatch(lang_tag=self.lang_tag)


class TransformCsvJadeBot(TransformCsvJadeBotTask):
    def get_rows(self, jade_bot):
        return [{"jade_bot_id": jade_bot["id"]}]


class TransformCsvJadeBotDescription(TransformCsvJadeBotTask):
    def get_rows(self, jade_bot):
        return [
            {
                "app_name": "gw2",
                "jade_bot_id": jade_bot["id"],
                "lang_tag": self.lang_tag.value,
                "original": common.to_xhmtl_fragment(jade_bot["description"]),
            }
        ]


class TransformCsvJadeBotItem(TransformCsvJadeBotTask):
    def get_rows(self, jade_bot):
        return [{"jade_bot_id": jade_bot["id"], "item_id": jade_bot["unlock_item"]}]


class TransformCsvJadeBotName(TransformCsvJadeBotTask):
    def get_rows(self, jade_bot):
        return [
            {
                "app_name": "gw2",
                "jade_bot_id": jade_bot["id"],
                "lang_tag": self.lang_tag.value,
                "original": common.to_xhmtl_fragment(jade_bot["name"]),
            }
        ]
