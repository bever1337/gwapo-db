import luigi

import common
import transform_csv
import transform_lang
import transform_patch_color


materials = ["cloth", "fur", "leather", "metal"]


class TransformColorTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        return transform_patch_color.TransformPatchColor(lang_tag=self.lang_tag)


class TransformColor(TransformColorTask):
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


class TransformColorBase(TransformColorTask):
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


class TransformColorName(TransformColorTask):
    def get_rows(self, color):
        return [
            {
                "app_name": "gw2",
                "color_id": color["id"],
                "lang_tag": self.lang_tag.value,
                "original": transform_lang.to_xhmtl_fragment(color["name"]),
            }
        ]


class TransformColorSample(TransformColorTask):
    def get_rows(self, color):
        color_id = color["id"]
        return [{"color_id": color_id, "material": material} for material in materials]


class TransformColorSampleAdjustment(TransformColorTask):
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


class TransformColorSampleShift(TransformColorTask):
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


class TransformColorSampleReference(TransformColorTask):
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
