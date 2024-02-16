import datetime
import luigi

import common
from tasks import transform_csv
import color_transform_patch


materials = ["cloth", "fur", "leather", "metal"]


class TransformCsvColorTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "color"

    def requires(self):
        return color_transform_patch.TransformPatch(lang_tag=self.lang_tag)


class TransformCsvColor(TransformCsvColorTask):
    def get_rows(self, color):
        color_categories = color["categories"]
        hue = (color_categories[0:1] or [None])[0]
        material = (color_categories[1:2] or [None])[0]
        rarity = (color_categories[2:3] or [None])[0]
        return [
            {
                "color_id": color["id"],
                "hue": hue,
                "material": material,
                "rarity": rarity,
            }
        ]


class TransformCsvColorBase(TransformCsvColorTask):
    def get_rows(self, color):
        base_rgb = color["base_rgb"]
        return [
            {
                "blue": base_rgb[2],
                "color_id": color["id"],
                "green": base_rgb[1],
                "red": base_rgb[0],
            }
        ]


class TransformCsvColorName(TransformCsvColorTask):
    app_name = luigi.Parameter(default="gw2")

    def get_rows(self, color):
        return [
            {
                "app_name": self.app_name,
                "color_id": color["id"],
                "lang_tag": self.lang_tag.value,
                "original": common.to_xhmtl_fragment(color["name"]),
            }
        ]


class TransformCsvColorNameTranslation(transform_csv.TransformCsvTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "color"
    translation_lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def get_rows(self, color):
        return [
            {
                "app_name": self.app_name,
                "color_id": color["id"],
                "original_lang_tag": self.original_lang_tag.value,
                "translation_lang_tag": self.translation_lang_tag.value,
                "translation": common.to_xhmtl_fragment(color["name"]),
            }
        ]

    def requires(self):
        return color_transform_patch.TransformPatch(lang_tag=self.translation_lang_tag)


class TransformCsvColorSample(TransformCsvColorTask):
    def get_rows(self, color):
        color_id = color["id"]
        return [{"color_id": color_id, "material": material} for material in materials]


class TransformCsvColorSampleAdjustment(TransformCsvColorTask):
    def get_rows(self, color):
        color_id = color["id"]
        return [
            {
                "brightness": color[material]["brightness"],
                "color_id": color_id,
                "contrast": color[material]["contrast"],
                "material": material,
            }
            for material in materials
        ]


class TransformCsvColorSampleShift(TransformCsvColorTask):
    def get_rows(self, color):
        color_id = color["id"]
        return [
            {
                "color_id": color_id,
                "hue": color[material]["hue"],
                "lightness": color[material]["lightness"],
                "material": material,
                "saturation": color[material]["saturation"],
            }
            for material in materials
        ]


class TransformCsvColorSampleReference(TransformCsvColorTask):
    def get_rows(self, color):
        color_id = color["id"]
        return [
            {
                "blue": color[material]["rgb"][2],
                "color_id": color_id,
                "green": color[material]["rgb"][1],
                "material": material,
                "red": color[material]["rgb"][0],
            }
            for material in materials
        ]
