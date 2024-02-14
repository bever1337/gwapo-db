import datetime
import luigi

import common
import profession_extract
from tasks import transform_csv


class TransformCsvProfessionTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
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
                "profession_id": profession["id"],
                "lang_tag": self.lang_tag.value,
                "original": common.to_xhmtl_fragment(profession["name"]),
            }
        ]
