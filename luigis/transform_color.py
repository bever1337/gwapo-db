import datetime
import enum
import luigi
from os import path

import common
import extract_batch
import transform_csv


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
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True)
    table = luigi.EnumParameter(enum=ColorTable)

    def output(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.csv".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        target_dir = "_".join(["transform", self.table.value])
        target_path = path.join(
            self.output_dir,
            target_dir,
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        return extract_batch.ExtractBatchTask(
            extract_datetime=self.extract_datetime,
            json_patch_path="./patch/color.json",
            json_schema_path="./schema/gw2/v2/colors/index.json",
            output_dir=self.output_dir,
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/colors",
        )

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
                        "original": color["name"],
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
            case ColorTable.ColorSampleReference:
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
            case ColorTable.ColorSampleReferencePerception:
                return []
            case _:
                raise RuntimeError("Unexpected table")
