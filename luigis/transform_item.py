import csv
import datetime
import enum
import json
import luigi
from os import path
from psycopg import sql

import common
import extract_batch
import load_profession
import load_race
import transform_csv


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


class TransformItem(transform_csv.TransformCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(exists=True)
    table = luigi.EnumParameter(enum=ItemTable)

    def output(self):
        output_folder_name = "_".join(["transform", self.table.value])
        return common.from_output_params(
            output_dir=path.join(self.output_dir, output_folder_name),
            extract_datetime=self.extract_datetime,
            params={"lang": self.lang_tag.value},
            ext="csv",
        )

    def requires(self):
        return {
            "item": extract_batch.ExtractBatchTask(
                extract_datetime=self.extract_datetime,
                json_schema_path="./schema/gw2/v2/items/index.json",
                output_dir=self.output_dir,
                url_params={"lang": self.lang_tag.value},
                url="https://api.guildwars2.com/v2/items",
            ),
            "race": load_race.LoadRace(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
            ),
            "profession": load_profession.LoadProfession(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
            ),
        }

    def get_rows(self, item, profession_ids: list[str], race_ids: list[str]):
        item_id = item["id"]
        match self.table:
            case ItemTable.Item:
                item_icon = item.get("icon")
                if item_icon == "":
                    item_icon = None
                return [
                    {
                        "chat_link": item["chat_link"],
                        "icon": item_icon,
                        "item_id": item_id,
                        "rarity": item["rarity"],
                        "required_level": item["level"],
                        "vendor_value": item["vendor_value"],
                    }
                ]
            case ItemTable.ItemDescription:
                item_description = item.get("description", "")
                if item_description == "":
                    return []
                return [
                    {
                        "app_name": "gw2",
                        "item_id": item_id,
                        "lang_tag": self.lang_tag.value,
                        "original": item_description,
                    }
                ]
            case ItemTable.ItemFlag:
                return [{"flag": flag, "item_id": item_id} for flag in item["flags"]]
            case ItemTable.ItemGameType:
                return [
                    {"game_type": game_type, "item_id": item_id}
                    for game_type in item["game_types"]
                ]
            case ItemTable.ItemName:
                item_name = item.get("name", "")
                if item_name == "":
                    return []
                return [
                    {
                        "app_name": "gw2",
                        "item_id": item_id,
                        "lang_tag": self.lang_tag.value,
                        "original": item_name,
                    }
                ]
            case ItemTable.ItemProfessionRestriction:
                return [
                    {"item_id": item_id, "profession_id": profession_id}
                    for profession_id in item["restrictions"]
                    if profession_id in profession_ids
                ]
            case ItemTable.ItemRaceRestriction:
                return [
                    {"item_id": item_id, "race_id": race_id}
                    for race_id in item["restrictions"]
                    if race_id in race_ids
                ]
            case ItemTable.ItemType:
                return [{"item_id": item_id, "item_type": item["type"]}]
            case ItemTable.ItemUpgrade:
                return [
                    *[
                        {
                            "from_item_id": upgrade_from["item_id"],
                            "to_item_id": item_id,
                            "upgrade": upgrade_from["upgrade"],
                        }
                        for upgrade_from in item.get("upgrades_from", [])
                    ],
                    *[
                        {
                            "from_item_id": item_id,
                            "to_item_id": upgrade_into["item_id"],
                            "upgrade": upgrade_into["upgrade"],
                        }
                        for upgrade_into in item.get("upgrades_into", [])
                    ],
                ]
            case _:
                raise RuntimeError("Unexpected table")

    def run(self):
        with common.get_conn() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql.SQL("SELECT race_id FROM gwapese.race;"))
                race_rows = cursor.fetchall()
                race_ids = [race_id for race_row in race_rows for race_id in race_row]
                cursor.execute(sql.SQL("SELECT profession_id FROM gwapese.profession;"))
                profession_rows = cursor.fetchall()
                profession_ids = [
                    profession_id
                    for profession_row in profession_rows
                    for profession_id in profession_row
                ]
        print("OK", race_ids, profession_ids)

        with (
            self.input().get("item").open("r") as r_input_file,
            self.output().open("w") as w_output_file,
        ):
            csv_writer = None
            for item_line in r_input_file:
                item = json.loads(item_line)

                rows = self.get_rows(
                    item=item, profession_ids=profession_ids, race_ids=race_ids
                )

                if len(rows) == 0:
                    continue

                if csv_writer is None:
                    peek_row = rows[0]
                    csv_writer = csv.DictWriter(
                        f=w_output_file, dialect="unix", fieldnames=peek_row.keys()
                    )
                    csv_writer.writeheader()
                csv_writer.writerows(rows)
