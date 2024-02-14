import datetime
import luigi

import common
import finisher_extract
from tasks import transform_csv


class TransformCsvFinisherTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "finisher"

    def requires(self):
        return finisher_extract.ExtractBatch(lang_tag=self.lang_tag)


class TransformCsvFinisher(TransformCsvFinisherTask):
    def get_rows(self, finisher):
        return [
            {
                "finisher_id": finisher["id"],
                "icon": finisher["icon"],
                "presentation_order": finisher["order"],
            }
        ]


class TransformCsvFinisherDetail(TransformCsvFinisherTask):
    def get_rows(self, finisher):
        unlock_details = finisher["unlock_details"]
        if unlock_details == "":
            return []
        return [
            {
                "app_name": "gw2",
                "finisher_id": finisher["id"],
                "lang_tag": self.lang_tag.value,
                "original": common.to_xhmtl_fragment(unlock_details),
            }
        ]


class TransformCsvFinisherItem(TransformCsvFinisherTask):
    def get_rows(self, finisher):
        finisher_id = finisher["id"]
        return [
            {"finisher_id": finisher_id, "item_id": item_id}
            for item_id in finisher["unlock_items"]
        ]


class TransformCsvFinisherName(TransformCsvFinisherTask):
    def get_rows(self, finisher):
        return [
            {
                "app_name": "gw2",
                "finisher_id": finisher["id"],
                "lang_tag": self.lang_tag.value,
                "original": common.to_xhmtl_fragment(finisher["name"]),
            }
        ]
