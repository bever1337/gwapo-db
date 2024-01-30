import datetime
import jsonschema
import json
import luigi
from os import path

import common
import extract_batch


class TransformSkin(luigi.Task):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)

    def output(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.ndjson".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        target_path = path.join(
            self.output_dir,
            "transform_skin",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        return extract_batch.ExtractBatchTask(
            extract_datetime=self.extract_datetime,
            json_schema_path="./schema/gw2/v2/skins/index.json",
            output_dir=self.output_dir,
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/skins",
        )

    def run(self):
        with (
            self.input().open("r") as r_input_file,
            self.output().open("w") as w_output_file,
        ):
            schema_validator = jsonschema.Draft202012Validator(skin_json_schema)

            for skin_line in r_input_file:
                skin = json.loads(skin_line)
                skin["description"] = skin.get("description")
                if skin["description"] == "":
                    skin["description"] = None

                skin["icon"] = skin.get("icon")
                if skin["icon"] == "":
                    skin["icon"] = None

                skin["name"] = skin.get("name")
                if skin["name"] == "":
                    skin["name"] = None

                schema_validator.validate(skin)
                w_output_file.write("".join([json.dumps(skin), "\n"]))


skin_json_schema = {
    "$defs": {
        "skin": {
            "properties": {
                "description": {
                    "oneOf": [{"minLength": 1, "type": "string"}, {"type": "null"}]
                },
                "flags": {
                    "items": {
                        "enum": [
                            "ShowInWardrobe",
                            "NoCost",
                            "HideIfLocked",
                            "OverrideRarity",
                        ]
                    },
                    "type": "array",
                },
                "icon": {
                    "oneOf": [
                        {"minLength": 1, "format": "uri", "type": "string"},
                        {"type": "null"},
                    ]
                },
                "id": {"type": "integer"},
                "name": {
                    "oneOf": [{"minLength": 1, "type": "string"}, {"type": "null"}]
                },
                "rarity": {"minLength": 1, "type": "string"},
                "restrictions": {
                    "items": {"minLength": 1, "type": "string"},
                    "type": "array",
                },
            },
            "required": [
                "description",
                "flags",
                "icon",
                "id",
                "name",
                "rarity",
                "restrictions",
            ],
            "type": "object",
        },
        "armor_skin": {
            "properties": {
                "details": {
                    "additionalProperties": False,
                    "properties": {
                        "dye_slots": {
                            "properties": {
                                "default": {
                                    "items": {
                                        "oneOf": [
                                            {"type": "null"},
                                            {
                                                "additionalProperties": False,
                                                "properties": {
                                                    "color_id": {"type": "integer"},
                                                    "material": {
                                                        "minLength": 1,
                                                        "type": "string",
                                                    },
                                                },
                                                "required": [
                                                    "color_id",
                                                    "material",
                                                ],
                                                "type": "object",
                                            },
                                        ]
                                    },
                                    "type": "array",
                                },
                                "overrides": {
                                    "additionalProperties": True,
                                    "properties": {},
                                    "type": "object",
                                },
                            },
                            "required": ["default"],
                            "type": "object",
                        },
                        "type": {"type": "string"},
                        "weight_class": {"type": "string"},
                    },
                    "required": ["type", "weight_class"],
                    "type": "object",
                },
                "type": {"const": "Armor"},
            },
            "required": ["details", "type"],
            "type": "object",
        },
        "back_skin": {
            "properties": {"type": {"const": "Back"}},
            "required": ["type"],
            "type": "object",
        },
        "gathering_skin": {
            "properties": {
                "details": {
                    "additionalProperties": False,
                    "properties": {"type": {"minLength": 1, "type": "string"}},
                    "required": ["type"],
                    "type": "object",
                },
                "type": {"const": "Gathering"},
            },
            "required": ["details", "type"],
            "type": "object",
        },
        "weapon_skin": {
            "properties": {
                "details": {
                    "additionalProperties": False,
                    "properties": {
                        "damage_type": {"minLength": 1, "type": "string"},
                        "type": {"minLength": 1, "type": "string"},
                    },
                    "required": ["damage_type", "type"],
                    "type": "object",
                },
                "type": {"const": "Weapon"},
            },
            "required": ["details", "type"],
            "type": "object",
        },
    },
    "allOf": [
        {"$ref": "#/$defs/skin"},
        {
            "oneOf": [
                {"$ref": "#/$defs/armor_skin"},
                {"$ref": "#/$defs/back_skin"},
                {"$ref": "#/$defs/gathering_skin"},
                {"$ref": "#/$defs/weapon_skin"},
            ]
        },
    ],
}
