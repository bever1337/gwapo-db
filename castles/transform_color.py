import enum
import luigi
from os import path

import common
import config
import transform_csv
import transform_lang
import transform_patch_color


class ColorTable(enum.Enum):
    Color = "color"
    ColorBase = "color_base"
    ColorName = "color_name"
    ColorSample = "color_sample"
    ColorSampleAdjustment = "color_sample_adjustment"
    ColorSampleShift = "color_sample_shift"
    ColorSampleReference = "color_sample_reference"
    ColorSampleReferencePerception = "color_sample_reference_perception"


materials = ["cloth", "fur", "leather", "metal"]


class TransformColor(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    table = luigi.EnumParameter(enum=ColorTable)

    def output(self):
        gwapo_config = config.gconfig()
        output_folder_name = "_".join(["transform", self.table.value])
        return common.from_output_params(
            output_dir=path.join(gwapo_config.output_dir, output_folder_name),
            extract_datetime=gwapo_config.extract_datetime,
            params={"lang": self.lang_tag.value},
            ext="csv",
        )

    def requires(self):
        return transform_patch_color.TransformPatchColor(lang_tag=self.lang_tag)

    def get_rows(self, color):
        color_id = color["id"]
        match self.table:
            case ColorTable.Color:
                color_categories = color["categories"]
                hue = (color_categories[0:1] or [None])[0]
                material = (color_categories[1:2] or [None])[0]
                rarity = (color_categories[2:3] or [None])[0]
                return [
                    {
                        "color_id": color_id,
                        "hue": hue,
                        "material": material,
                        "rarity": rarity,
                    }
                ]
            case ColorTable.ColorBase:
                return [
                    {
                        "blue": color["base_rgb"][2],
                        "color_id": color_id,
                        "green": color["base_rgb"][1],
                        "red": color["base_rgb"][0],
                    }
                ]
            case ColorTable.ColorName:
                return [
                    {
                        "app_name": "gw2",
                        "color_id": color_id,
                        "lang_tag": self.lang_tag.value,
                        "original": transform_lang.to_xhmtl_fragment(color["name"]),
                    }
                ]
            case ColorTable.ColorSample:
                return [
                    {"color_id": color_id, "material": material}
                    for material in materials
                ]
            case ColorTable.ColorSampleAdjustment:
                return [
                    {
                        "brightness": color[material]["brightness"],
                        "color_id": color_id,
                        "contrast": color[material]["contrast"],
                        "material": material,
                    }
                    for material in materials
                ]
            case ColorTable.ColorSampleShift:
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
            case (
                ColorTable.ColorSampleReference
                | ColorTable.ColorSampleReferencePerception
            ):
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
            case _:
                raise RuntimeError("Unexpected table")
