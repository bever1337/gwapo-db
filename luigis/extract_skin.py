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
import extract_skin_id


class ExtractSkin(luigi.Task):
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
            "extract_skin",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        return extract_skin_id.ExtractSkinId(extract_datetime=self.extract_datetime)

    def run(self):
        input_target: luigi.LocalTarget = self.input()
        with input_target.open("r") as input_file:
            skin_id_json: typing.List[int] = json.load(input_file)

        skins: typing.List = []

        for skin_id_batch in itertools.batched(skin_id_json, 200):
            ids_param = ",".join(str(skin_id) for skin_id in skin_id_batch)
            skins_response = requests.get(
                url="https://api.guildwars2.com/v2/skins",
                params={"ids": ids_param, "lang": self.lang_tag.value},
            )
            if skins_response.status_code != 200:
                raise RuntimeError("Expected status code 200")
            skins_json = skins_response.json()
            jsonschema.validate(
                instance=skins_json,
                schema=v2_skins_schema,
            )
            skins.extend(skins_json)
            time.sleep(1 / 7)

        with self.output().open("w") as write_target:
            json.dump(obj=skins, fp=write_target)


v2_skins_schema = {
    "$defs": {
        "skin": {
            "properties": {
                "description": {"type": "string"},
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
                "icon": {"format": "uri", "type": "string"},
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "rarity": {"type": "string"},
                "restrictions": {
                    "items": {"type": "string"},
                    "type": "array",
                },
            },
            "required": [
                "flags",
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
                                                    "material": {"type": "string"},
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
                    "properties": {"type": {"type": "string"}},
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
                        "damage_type": {"type": "string"},
                        "type": {"type": "string"},
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
    "items": {
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
    },
    "type": "array",
}
