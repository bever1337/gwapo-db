import luigi

import common
import profession_extract
from tasks import config
from tasks import transform_csv


class TransformCsvProfessionTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "profession"

    def requires(self):
        return profession_extract.ExtractBatch(lang_tag=self.lang_tag)


class TransformCsvProfession(TransformCsvProfessionTask):
    def get_rows(self, profession):
        return [
            {
                "code": profession["code"],
                "icon_big": profession["icon_big"],
                "icon": profession["icon"],
                "profession_id": profession["id"],
            }
        ]


class TransformCsvProfessionName(TransformCsvProfessionTask):
    def get_rows(self, profession):
        return [
            {
                "app_name": "gw2",
                "lang_tag": self.lang_tag.value,
                "original": common.to_xhmtl_fragment(profession["name"]),
                "profession_id": profession["id"],
            }
        ]


class TransformCsvProfessionNameTranslation(transform_csv.TransformCsvTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "profession"
    translation_lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def get_rows(self, profession):
        return [
            {
                "app_name": self.app_name,
                "original_lang_tag": self.original_lang_tag.value,
                "profession_id": profession["id"],
                "translation_lang_tag": self.translation_lang_tag.value,
                "translation": common.to_xhmtl_fragment(profession["name"]),
            }
        ]

    def requires(self):
        return profession_extract.ExtractBatch(lang_tag=self.translation_lang_tag)
