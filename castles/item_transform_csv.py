import csv
import datetime
import json
import luigi
from psycopg import sql

import common
import item_extract
import profession_load_csv
import race_load_csv
from tasks import transform_csv


class TransformCsvItemTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "item"

    def requires(self):
        return {
            "item": item_extract.ExtractBatch(lang_tag=self.lang_tag),
            "race": race_load_csv.LoadCsvRace(lang_tag=self.lang_tag),
            "profession": profession_load_csv.LoadCsvProfession(lang_tag=self.lang_tag),
        }

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


class TransformCsvItem(TransformCsvItemTask):
    def get_rows(self, item, profession_ids: list[str], race_ids: list[str]):
        item_icon = item.get("icon")
        if item_icon == "":
            item_icon = None
        return [
            {
                "chat_link": item["chat_link"],
                "icon": item_icon,
                "item_id": item["id"],
                "rarity": item["rarity"],
                "required_level": item["level"],
                "vendor_value": item["vendor_value"],
            }
        ]


class TransformCsvItemDescription(TransformCsvItemTask):
    def get_rows(self, item, profession_ids: list[str], race_ids: list[str]):
        item_description = item.get("description", "")
        if item_description == "":
            return []
        return [
            {
                "app_name": "gw2",
                "item_id": item["id"],
                "lang_tag": self.lang_tag.value,
                "original": common.to_xhmtl_fragment(item_description),
            }
        ]


class TransformCsvItemFlag(TransformCsvItemTask):
    def get_rows(self, item, profession_ids: list[str], race_ids: list[str]):
        item_id = item["id"]
        return [{"flag": flag, "item_id": item_id} for flag in item["flags"]]


class TransformCsvItemGameType(TransformCsvItemTask):
    def get_rows(self, item, profession_ids: list[str], race_ids: list[str]):
        item_id = item["id"]
        return [
            {"game_type": game_type, "item_id": item_id}
            for game_type in item["game_types"]
        ]


class TransformCsvItemName(TransformCsvItemTask):
    def get_rows(self, item, profession_ids: list[str], race_ids: list[str]):
        item_name = item.get("name", "")
        if item_name == "":
            return []
        return [
            {
                "app_name": "gw2",
                "item_id": item["id"],
                "lang_tag": self.lang_tag.value,
                "original": common.to_xhmtl_fragment(item_name),
            }
        ]


class TransformCsvItemRestrictionProfession(TransformCsvItemTask):
    def get_rows(self, item, profession_ids: list[str], race_ids: list[str]):
        item_id = item["id"]
        return [
            {"item_id": item_id, "profession_id": profession_id}
            for profession_id in item["restrictions"]
            if profession_id in profession_ids
        ]


class TransformCsvItemRestrictionRace(TransformCsvItemTask):
    def get_rows(self, item, profession_ids: list[str], race_ids: list[str]):
        item_id = item["id"]
        return [
            {"item_id": item_id, "race_id": race_id}
            for race_id in item["restrictions"]
            if race_id in race_ids
        ]


class TransformCsvItemType(TransformCsvItemTask):
    def get_rows(self, item, profession_ids: list[str], race_ids: list[str]):
        return [{"item_id": item["id"], "item_type": item["type"]}]


class TransformCsvItemUpgrade(TransformCsvItemTask):
    def get_rows(self, item, profession_ids: list[str], race_ids: list[str]):
        item_id = item["id"]
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


class TransformCsvItemDefaultSkin(TransformCsvItemTask):
    def get_rows(self, item, profession_ids: list[str], race_ids: list[str]):
        default_skin = item.get("default_skin")
        if default_skin is None:
            return []
        return [{"item_id": item["id"], "skin_id": default_skin}]