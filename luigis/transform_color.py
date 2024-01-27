import datetime
import jsonschema
import json
import luigi
from os import path

import common
import extract_batch


class TransformColor(luigi.Task):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True)

    def output(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.ndjson".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        target_path = path.join(
            self.output_dir,
            "transform_color",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        return extract_batch.ExtractBatch(
            entity_schema="../schema/gw2/v2/colors/color.json",
            extract_datetime=self.extract_datetime,
            id_schema="../schema/gw2/v2/colors/index.json",
            output_dir=self.output_dir,
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/colors",
        )

    def run(self):
        schema_validator = jsonschema.Draft202012Validator(color_schema)
        with (
            self.input().open("r") as r_input_file,
            self.output().open("w") as w_output_file,
        ):
            for color_line in r_input_file:
                color = json.loads(color_line)
                if color["id"] == 1594:
                    color["fur"] = color["cloth"]
                schema_validator.validate(color)
                w_output_file.write("".join([json.dumps(color), "\n"]))


color_schema = {
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
        "fur",
        "id",
        "leather",
        "metal",
        "name",
    ],
    "type": "object",
}
