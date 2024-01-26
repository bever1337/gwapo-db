import datetime
import jsonschema
import json
import luigi
from os import path

import common
import extract_batch


class TransformItem(luigi.Task):
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
            "transform_item",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.json".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        return extract_batch.ExtractBatch(
            entity_schema="../schema/gw2/v2/items/item.json",
            extract_datetime=self.extract_datetime,
            extract_dir=path.join(self.output_dir, "extract_item_id"),
            id_schema="../schema/gw2/v2/items/index.json",
            output_file=path.join(
                self.output_dir,
                "extract_item",
                target_filename,
            ),
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/items",
        )

    def run(self):
        with self.input().open("r") as input_item_file:
            input_item_json: list[dict] = json.load(fp=input_item_file)

        schema_validator = jsonschema.Draft202012Validator(item_json_schema)
        for item in input_item_json:
            item["description"] = item.get("description")
            if item["description"] == "":
                item["description"] = None

            item["icon"] = item.get("icon")
            if item["icon"] == "":
                item["icon"] = None

            item["name"] = item.get("name")
            if item["name"] == "":
                item["name"] = None

            item["upgrades_from"] = item.get("upgrades_from", [])
            item["upgrades_into"] = item.get("upgrades_into", [])

            schema_validator.validate(item)

        with self.output().open("w") as w_output_file:
            json.dump(obj=input_item_json, fp=w_output_file)


item_json_schema = {
    "$id": "schema/gw2/v2/items/items.json",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "properties": {
        "chat_link": {"format": "uri", "minLength": 1, "type": "string"},
        "default_skin": {"type": "integer"},
        "description": {
            "oneOf": [{"minLength": 1, "type": "string"}, {"type": "null"}],
        },
        "details": {"type": "object"},
        "flags": {"items": {"minLength": 1, "type": "string"}, "type": "array"},
        "game_types": {"items": {"minLength": 1, "type": "string"}, "type": "array"},
        "icon": {
            "oneOf": [
                {"format": "uri", "minLength": 1, "type": "string"},
                {"type": "null"},
            ],
        },
        "id": {"type": "integer"},
        "name": {
            "oneOf": [{"minLength": 1, "type": "string"}, {"type": "null"}],
        },
        "level": {"type": "integer"},
        "rarity": {"minLength": 1, "type": "string"},
        "restrictions": {"items": {"minLength": 1, "type": "string"}, "type": "array"},
        "type": {"minLength": 1, "type": "string"},
        "upgrades_from": {
            "items": {
                "parameters": {
                    "upgrade": {"minLength": 1, "type": "string"},
                    "item_id": {"format": "integer"},
                },
                "required": ["upgrade", "item_id"],
                "type": "object",
            },
            "type": "array",
        },
        "upgrades_into": {
            "items": {
                "parameters": {
                    "upgrade": {"minLength": 1, "type": "string"},
                    "item_id": {"format": "integer"},
                },
                "required": ["upgrade", "item_id"],
                "type": "object",
            },
            "type": "array",
        },
        "vendor_value": {"type": "integer"},
    },
    "required": [
        "chat_link",
        "description",
        "flags",
        "game_types",
        "icon",
        "id",
        "name",
        "level",
        "rarity",
        "restrictions",
        "type",
        "upgrades_from",
        "upgrades_into",
        "vendor_value",
    ],
    "type": "object",
}
