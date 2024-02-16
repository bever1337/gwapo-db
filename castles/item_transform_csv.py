import datetime
import luigi

import common
import item_extract
from tasks import transform_csv


class TransformCsvItemTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "item"

    def requires(self):
        return item_extract.ExtractBatch(lang_tag=self.lang_tag)


class TransformCsvItem(TransformCsvItemTask):
    def get_rows(self, item):
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
    def get_rows(self, item):
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
    def get_rows(self, item):
        item_id = item["id"]
        return [{"flag": flag, "item_id": item_id} for flag in item["flags"]]


class TransformCsvItemGameType(TransformCsvItemTask):
    def get_rows(self, item):
        item_id = item["id"]
        return [
            {"game_type": game_type, "item_id": item_id}
            for game_type in item["game_types"]
        ]


class TransformCsvItemName(TransformCsvItemTask):
    def get_rows(self, item):
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


class TransformCsvItemRestriction(TransformCsvItemTask):
    def get_rows(self, item):
        item_id = item["id"]
        return [
            {"item_id": item_id, "restriction_id": restriction_id}
            for restriction_id in item["restrictions"]
        ]


class TransformCsvItemType(TransformCsvItemTask):
    def get_rows(self, item):
        return [{"item_id": item["id"], "item_type": item["type"]}]


class TransformCsvItemUpgrade(TransformCsvItemTask):
    def get_rows(self, item):
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
    def get_rows(self, item):
        default_skin = item.get("default_skin")
        if default_skin is None:
            return []
        return [{"item_id": item["id"], "skin_id": default_skin}]
