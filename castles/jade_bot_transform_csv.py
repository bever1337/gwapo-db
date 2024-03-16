import luigi

import common
import jade_bot_extract
from tasks import config
from tasks import transform_csv


class TransformCsvJadeBotTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "jade_bot"

    def requires(self):
        return jade_bot_extract.ExtractBatch(lang_tag=self.lang_tag)


class TransformCsvJadeBot(TransformCsvJadeBotTask):
    def get_rows(self, jade_bot):
        return [{"jade_bot_id": jade_bot["id"]}]


class TransformCsvJadeBotDescription(TransformCsvJadeBotTask):
    def get_rows(self, jade_bot):
        jade_bot_description = jade_bot["description"]
        if jade_bot_description == "":
            return []
        return [
            {
                "app_name": "gw2",
                "jade_bot_id": jade_bot["id"],
                "lang_tag": self.lang_tag.value,
                "original": common.to_xhmtl_fragment(jade_bot_description),
            }
        ]


class TransformCsvJadeBotDescriptionTranslation(transform_csv.TransformCsvTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "jade_bot"
    translation_lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def get_rows(self, jade_bot):
        jade_bot_description = jade_bot["description"]
        if jade_bot_description == "":
            return []
        return [
            {
                "app_name": self.app_name,
                "jade_bot_id": jade_bot["id"],
                "original_lang_tag": self.original_lang_tag.value,
                "translation_lang_tag": self.translation_lang_tag.value,
                "translation": common.to_xhmtl_fragment(jade_bot_description),
            }
        ]

    def requires(self):
        return jade_bot_extract.ExtractBatch(lang_tag=self.translation_lang_tag)


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


class TransformCsvJadeBotNameTranslation(transform_csv.TransformCsvTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "jade_bot"
    translation_lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def get_rows(self, jade_bot):
        return [
            {
                "app_name": self.app_name,
                "jade_bot_id": jade_bot["id"],
                "original_lang_tag": self.original_lang_tag.value,
                "translation_lang_tag": self.translation_lang_tag.value,
                "translation": common.to_xhmtl_fragment(jade_bot["name"]),
            }
        ]

    def requires(self):
        return jade_bot_extract.ExtractBatch(lang_tag=self.translation_lang_tag)
