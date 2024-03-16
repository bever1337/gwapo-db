import luigi

import common
import outfit_extract
from tasks import config
from tasks import transform_csv


class TransformCsvOutfitTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "outfit"

    def requires(self):
        return outfit_extract.ExtractBatch(lang_tag=self.lang_tag)


class TransformCsvOutfit(TransformCsvOutfitTask):
    def get_rows(self, outfit):
        return [{"icon": outfit["icon"], "outfit_id": outfit["id"]}]


class TransformCsvOutfitItem(TransformCsvOutfitTask):
    def get_rows(self, outfit):
        outfit_id = outfit["id"]
        return [
            {"item_id": item_id, "outfit_id": outfit_id}
            for item_id in outfit["unlock_items"]
        ]


class TransformCsvOutfitName(TransformCsvOutfitTask):
    def get_rows(self, outfit):
        return [
            {
                "app_name": "gw2",
                "outfit_id": outfit["id"],
                "lang_tag": self.lang_tag.value,
                "original": common.to_xhmtl_fragment(outfit["name"]),
            }
        ]


class TransformCsvOutfitNameTranslation(transform_csv.TransformCsvTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "outfit"
    translation_lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def get_rows(self, outfit):
        return [
            {
                "app_name": self.app_name,
                "original_lang_tag": self.original_lang_tag.value,
                "outfit_id": outfit["id"],
                "translation_lang_tag": self.translation_lang_tag.value,
                "translation": common.to_xhmtl_fragment(outfit["name"]),
            }
        ]

    def requires(self):
        return outfit_extract.ExtractBatch(lang_tag=self.translation_lang_tag)
