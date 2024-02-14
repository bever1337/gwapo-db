import datetime
import luigi

import common
import specialization_extract
from tasks import transform_csv


class TransformCsvSpecializationTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
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
                "specialization_id": specialization["id"],
                "lang_tag": self.lang_tag.value,
                "original": common.to_xhmtl_fragment(specialization["name"]),
            }
        ]
