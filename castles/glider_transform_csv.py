import datetime
import luigi

import common
import glider_extract
from tasks import transform_csv


class TransformCsvGliderTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "glider"

    def requires(self):
        return glider_extract.ExtractBatch(lang_tag=self.lang_tag)


class TransformCsvGlider(TransformCsvGliderTask):
    def get_rows(self, glider):
        return [
            {
                "glider_id": glider["id"],
                "icon": glider["icon"],
                "presentation_order": glider["order"],
            }
        ]


class TransformCsvGliderDescription(TransformCsvGliderTask):
    def get_rows(self, glider):
        glider_description = glider["description"]
        if glider_description == "":
            return []
        return [
            {
                "app_name": "gw2",
                "glider_id": glider["id"],
                "lang_tag": self.lang_tag.value,
                "original": common.to_xhmtl_fragment(glider_description),
            }
        ]


class TransformCsvGliderDyeSlot(TransformCsvGliderTask):
    def get_rows(self, glider):
        glider_id = glider["id"]
        return [
            {
                "color_id": color_id,
                "glider_id": glider_id,
                "slot_index": index,
            }
            for index, color_id in enumerate(glider["default_dyes"])
        ]


class TransformCsvGliderItem(TransformCsvGliderTask):
    def get_rows(self, glider):
        glider_id = glider["id"]
        return [
            {"glider_id": glider_id, "item_id": item_id}
            for item_id in glider.get("unlock_items", [])
        ]


class TransformCsvGliderName(TransformCsvGliderTask):
    def get_rows(self, glider):
        return [
            {
                "app_name": "gw2",
                "glider_id": glider["id"],
                "lang_tag": self.lang_tag.value,
                "original": common.to_xhmtl_fragment(glider["name"]),
            }
        ]
