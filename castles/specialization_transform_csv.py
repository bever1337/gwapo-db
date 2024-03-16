import luigi

import common
import specialization_extract
from tasks import config
from tasks import transform_csv


class TransformCsvSpecializationTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "specialization"

    def requires(self):
        return specialization_extract.ExtractBatch(lang_tag=self.lang_tag)


class TransformCsvSpecialization(TransformCsvSpecializationTask):
    def get_rows(self, specialization):
        return [
            {
                "background": specialization["background"],
                "elite": specialization["elite"],
                "icon": specialization["icon"],
                "profession_id": specialization["profession"],
                "specialization_id": specialization["id"],
            }
        ]


class TransformCsvSpecializationName(TransformCsvSpecializationTask):
    def get_rows(self, specialization):
        return [
            {
                "app_name": "gw2",
                "lang_tag": self.lang_tag.value,
                "original": common.to_xhmtl_fragment(specialization["name"]),
                "specialization_id": specialization["id"],
            }
        ]


class TransformCsvSpecializationNameTranslation(transform_csv.TransformCsvTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "specialization"
    translation_lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def get_rows(self, specialization):
        return [
            {
                "app_name": self.app_name,
                "original_lang_tag": self.original_lang_tag.value,
                "specialization_id": specialization["id"],
                "translation_lang_tag": self.translation_lang_tag.value,
                "translation": common.to_xhmtl_fragment(specialization["name"]),
            }
        ]

    def requires(self):
        return specialization_extract.ExtractBatch(lang_tag=self.translation_lang_tag)
