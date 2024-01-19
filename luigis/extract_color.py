import datetime
import itertools
import jsonschema
import json
import luigi
from os import path
import requests
import time
import typing

import common
import extract_color_id


class ExtractColor(luigi.Task):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)

    def output(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.json".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        target_path = path.join(
            self.output_dir,
            "extract_color",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        return extract_color_id.ExtractColorId(extract_datetime=self.extract_datetime)

    def run(self):
        input_target: luigi.LocalTarget = self.input()
        with input_target.open("r") as input_file:
            color_id_json: typing.List[int] = json.load(input_file)

        colors: typing.List = []

        for color_id_batch in itertools.batched(color_id_json, 200):
            ids_param = ",".join(str(color_id) for color_id in color_id_batch)
            colors_response = requests.get(
                url="https://api.guildwars2.com/v2/colors",
                params={"ids": ids_param, "lang": self.lang_tag.value},
            )
            if colors_response.status_code != 200:
                raise RuntimeError("Expected status code 200")
            colors_json = colors_response.json()
            jsonschema.validate(
                instance=colors_json,
                schema=v2_colors_schema,
            )
            colors.extend(colors_json)
            time.sleep(1 / 7)

        with self.output().open("w") as write_target:
            json.dump(obj=colors, fp=write_target)


v2_colors_schema = {
    "$defs": {
        "details": {
            "properties": {
                "brightness": {"type": "integer"},
                "contrast": {"type": "number"},
                "hue": {"type": "number"},
                "lightness": {"type": "number"},
                "rgb": {
                    "items": {"type": "integer"},
                    "maxItems": 3,
                    "minItems": 3,
                    "type": "array",
                },
                "saturation": {"type": "number"},
            },
            "required": [
                "brightness",
                "contrast",
                "hue",
                "lightness",
                "rgb",
                "saturation",
            ],
            "type": "object",
        }
    },
    "items": {
        "properties": {
            "base_rgb": {
                "prefixItems": [
                    {"type": "integer"},
                    {"type": "integer"},
                    {"type": "integer"},
                ],
                "type": "array",
            },
            "categories": {
                "prefixItems": [
                    {"type": "string"},
                    {"type": "string"},
                    {"type": "string"},
                ],
                "type": "array",
            },
            "cloth": {"$ref": "#/$defs/details"},
            "fur": {"$ref": "#/$defs/details"},
            "id": {"type": "integer"},
            "item": {"type": "integer"},
            "leather": {"$ref": "#/$defs/details"},
            "metal": {"$ref": "#/$defs/details"},
            "name": {"type": "string"},
        },
        "required": [
            "base_rgb",
            "categories",
            "cloth",
            "id",
            "leather",
            "metal",
            "name",
        ],
        "type": "object",
    },
    "type": "array",
}
