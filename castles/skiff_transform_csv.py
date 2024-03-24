import luigi

import common
import skiff_extract
from tasks import config
from tasks import transform_csv


class TransformCsvSkiffTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "skiff"

    def requires(self):
        return skiff_extract.ExtractBatch(lang_tag=self.lang_tag)


class TransformCsvSkiff(TransformCsvSkiffTask):
    def get_rows(self, skiff):
        return [{"icon": skiff["icon"], "skiff_id": skiff["id"]}]


class TransformCsvSkiffDyeSlot(TransformCsvSkiffTask):
    def get_rows(self, skiff):
        skiff_id = skiff["id"]
        return [
            {
                "color_id": dye_slot["color_id"],
                "material": dye_slot["material"],
                "skiff_id": skiff_id,
                "slot_index": slot_index,
            }
            for slot_index, dye_slot in enumerate(skiff["dye_slots"])
        ]


class TransformCsvSkiffName(TransformCsvSkiffTask):
    def get_rows(self, skiff):
        return [
            {
                "app_name": "gw2",
                "lang_tag": self.lang_tag.value,
                "original": common.to_xhmtl_fragment(skiff["name"]),
                "skiff_id": skiff["id"],
            }
        ]


class TransformCsvSkiffNameTranslation(transform_csv.TransformCsvTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "skiff"
    translation_lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def get_rows(self, skiff):
        return [
            {
                "app_name": self.app_name,
                "original_lang_tag": self.original_lang_tag.value,
                "skiff_id": skiff["id"],
                "translation_lang_tag": self.translation_lang_tag.value,
                "translation": common.to_xhmtl_fragment(skiff["name"]),
            }
        ]

    def requires(self):
        return skiff_extract.ExtractBatch(lang_tag=self.translation_lang_tag)
