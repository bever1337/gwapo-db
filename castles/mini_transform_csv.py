import datetime
import luigi

import common
import mini_transform_patch
from tasks import transform_csv


class TransformCsvMiniTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "mini"

    def requires(self):
        return mini_transform_patch.TransformPatch(lang_tag=self.lang_tag)


class TransformCsvMini(TransformCsvMiniTask):
    def get_rows(self, mini):
        return [
            {
                "icon": mini["icon"],
                "mini_id": mini["id"],
                "presentation_order": mini["order"],
            }
        ]


class TransformCsvMiniItem(TransformCsvMiniTask):
    def get_rows(self, mini):
        return [{"item_id": mini["item_id"], "mini_id": mini["id"]}]


class TransformCsvMiniName(TransformCsvMiniTask):
    def get_rows(self, mini):
        return [
            {
                "app_name": "gw2",
                "lang_tag": self.lang_tag.value,
                "mini_id": mini["id"],
                "original": common.to_xhmtl_fragment(mini["name"]),
            }
        ]


class TransformCsvMiniUnlock(TransformCsvMiniTask):
    def get_rows(self, mini):
        mini_unlock = mini.get("unlock")
        if mini_unlock == None:
            return []
        return [
            {
                "app_name": "gw2",
                "lang_tag": self.lang_tag.value,
                "mini_id": mini["id"],
                "original": common.to_xhmtl_fragment(mini_unlock),
            }
        ]
