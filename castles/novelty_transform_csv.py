import luigi

import common
import novelty_extract
from tasks import config
from tasks import transform_csv


class TransformCsvNoveltyTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "novelty"

    def requires(self):
        return novelty_extract.ExtractBatch(lang_tag=self.lang_tag)


class TransformCsvNovelty(TransformCsvNoveltyTask):
    def get_rows(self, novelty):
        return [
            {
                "icon": novelty["icon"],
                "novelty_id": novelty["id"],
                "slot": novelty["slot"],
            }
        ]


class TransformCsvNoveltyDescription(TransformCsvNoveltyTask):
    def get_rows(self, novelty):
        novelty_description = novelty["description"]
        if novelty_description == "":
            return []
        return [
            {
                "app_name": "gw2",
                "lang_tag": self.lang_tag.value,
                "novelty_id": novelty["id"],
                "original": common.to_xhmtl_fragment(novelty_description),
            }
        ]


class TransformCsvNoveltyDescriptionTranslation(transform_csv.TransformCsvTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "novelty"
    translation_lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def get_rows(self, novelty):
        novelty_description = novelty["description"]
        if novelty_description == "":
            return []
        return [
            {
                "app_name": self.app_name,
                "novelty_id": novelty["id"],
                "original_lang_tag": self.original_lang_tag.value,
                "translation_lang_tag": self.translation_lang_tag.value,
                "translation": common.to_xhmtl_fragment(novelty_description),
            }
        ]

    def requires(self):
        return novelty_extract.ExtractBatch(lang_tag=self.translation_lang_tag)


class TransformCsvNoveltyItem(TransformCsvNoveltyTask):
    def get_rows(self, novelty):
        novelty_id = novelty["id"]
        return [
            {"item_id": item_id, "novelty_id": novelty_id}
            for item_id in novelty["unlock_item"]
        ]


class TransformCsvNoveltyName(TransformCsvNoveltyTask):
    def get_rows(self, novelty):
        return [
            {
                "app_name": "gw2",
                "lang_tag": self.lang_tag.value,
                "novelty_id": novelty["id"],
                "original": common.to_xhmtl_fragment(novelty["name"]),
            }
        ]


class TransformCsvNoveltyNameTranslation(transform_csv.TransformCsvTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "novelty"
    translation_lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def get_rows(self, novelty):
        return [
            {
                "app_name": self.app_name,
                "novelty_id": novelty["id"],
                "original_lang_tag": self.original_lang_tag.value,
                "translation_lang_tag": self.translation_lang_tag.value,
                "translation": common.to_xhmtl_fragment(novelty["name"]),
            }
        ]

    def requires(self):
        return novelty_extract.ExtractBatch(lang_tag=self.translation_lang_tag)
