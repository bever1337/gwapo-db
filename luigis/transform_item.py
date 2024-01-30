import csv
import datetime
import enum
import jsonschema
import json
import luigi
from os import path

import common
import extract_batch
import extract_race


class ItemTable(enum.Enum):
    Item = "item"
    ItemDescription = "item_description"
    ItemFlag = "item_flag"
    ItemGameType = "item_game_type"
    ItemName = "item_name"
    ItemProfessionRestriction = "item_profession_restriction"
    ItemRaceRestriction = "item_race_restriction"
    ItemType = "item_type"
    ItemUpgrade = "item_upgrade"


class TransformItem(luigi.Task):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)
    table = luigi.EnumParameter(enum=ItemTable)

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
        return {
            "item": extract_batch.ExtractBatchTask(
                extract_datetime=self.extract_datetime,
                json_schema_path="./schema/gw2/v2/items/index.json",
                output_dir=self.output_dir,
                url_params={"lang": self.lang_tag.value},
                url="https://api.guildwars2.com/v2/items",
            ),
            "profession": extract_batch.ExtractBatchTask(
                extract_datetime=self.extract_datetime,
                json_schema_path="./schema/gw2/v2/professions/index.json",
                output_dir=self.output_dir,
                url_params={
                    "lang": self.lang_tag.value,
                    "v": "2019-12-19T00:00:00.000Z",
                },
                url="https://api.guildwars2.com/v2/professions",
            ),
            "race": extract_race.ExtractRace(extract_datetime=self.extract_datetime),
        }

    def run(self):
        inputs = self.input()

        with inputs["profession"].open("r") as ro_input_file:
            professions: list[str] = [json.loads(line)["id"] for line in ro_input_file]

        with inputs["race"].open("r") as ro_input_file:
            race_names: list[str] = json.load(fp=ro_input_file)

        with (
            inputs["item"].open("r") as r_input_file,
            self.output().open("w") as w_output_file,
        ):
            schema_validator = jsonschema.Draft202012Validator(item_json_schema)
            csv_writer = None
            for item_line in r_input_file:
                item = json.loads(item_line)
                item_id = item["id"]

                item["description"] = item.get("description", "")
                item["icon"] = item.get("icon")
                if item["icon"] == "":
                    item["icon"] = None
                item["name"] = item.get("name", "")
                item["upgrades_from"] = item.get("upgrades_from", [])
                item["upgrades_into"] = item.get("upgrades_into", [])
                schema_validator.validate(item)

                rows: list[dict] = []
                match self.table:
                    case ItemTable.Item:
                        rows.append(
                            {
                                "chat_link": item["chat_link"],
                                "icon": item["icon"],
                                "item_id": item_id,
                                "rarity": item["rarity"],
                                "required_level": item["level"],
                                "vendor_value": item["vendor_value"],
                            }
                        )
                    case ItemTable.ItemDescription:
                        item_description = item["description"]
                        if item_description != "":
                            rows.append(
                                {
                                    "app_name": "gw2",
                                    "item_id": item_id,
                                    "lang_tag": self.lang_tag.value,
                                    "original": item_description,
                                }
                            )
                    case ItemTable.ItemFlag:
                        rows.extend(
                            {"flag": flag, "item_id": item_id} for flag in item["flags"]
                        )
                    case ItemTable.ItemGameType:
                        rows.extend(
                            {"game_type": game_type, "item_id": item_id}
                            for game_type in item["game_types"]
                        )
                    case ItemTable.ItemName:
                        item_name = item["name"]
                        if item_name != "":
                            rows.append(
                                {
                                    "app_name": "gw2",
                                    "item_id": item_id,
                                    "lang_tag": self.lang_tag.value,
                                    "original": item_name,
                                }
                            )
                    case ItemTable.ItemProfessionRestriction:
                        rows.extend(
                            [
                                {"item_id": item_id, "profession_id": profession_id}
                                for profession_id in item["restrictions"]
                                if profession_id in professions
                            ]
                        )
                    case ItemTable.ItemRaceRestriction:
                        rows.extend(
                            [
                                {"item_id": item_id, "race_name": race_name}
                                for race_name in item["restrictions"]
                                if race_name in race_names
                            ]
                        )
                    case ItemTable.ItemType:
                        rows.append({"item_id": item_id, "item_type": item["type"]})
                    case ItemTable.ItemUpgrade:
                        """"""
                    case _:
                        raise RuntimeError("Unexpected table")

                if len(rows) == 0:
                    continue

                if csv_writer is None:
                    peek_row = rows[0]
                    csv_writer = csv.DictWriter(
                        f=w_output_file, dialect="unix", fieldnames=peek_row.keys()
                    )
                    csv_writer.writeheader()
                csv_writer.writerows(rows)


item_json_schema = {
    "$id": "gw2/v2/items/items.json",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "properties": {
        "chat_link": {"format": "uri", "minLength": 1, "type": "string"},
        "default_skin": {"type": "integer"},
        "description": {"type": "string"},
        "details": {"type": "object"},
        "flags": {"items": {"minLength": 1, "type": "string"}, "type": "array"},
        "game_types": {"items": {"minLength": 1, "type": "string"}, "type": "array"},
        "icon": {
            "oneOf": [
                {"minLength": 1, "format": "uri", "type": "string"},
                {"type": "null"},
            ]
        },
        "id": {"type": "integer"},
        "name": {"type": "string"},
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
