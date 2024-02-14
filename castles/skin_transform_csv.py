import datetime
import luigi

import common
import skin_extract
from tasks import transform_csv


class TransformCsvSkinTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "skin"

    def requires(self):
        return skin_extract.ExtractBatch(lang_tag=self.lang_tag)


class TransformCsvSkin(TransformCsvSkinTask):
    def get_rows(self, skin):
        skin_icon = skin.get("icon")
        if skin_icon == "":
            skin_icon = None
        return [{"icon": skin_icon, "rarity": skin["rarity"], "skin_id": skin["id"]}]


class TransformCsvSkinArmor(TransformCsvSkinTask):
    def get_rows(self, skin):
        if skin["type"] != "Armor":
            return []
        details = skin["details"]
        return [
            {
                "skin_id": skin["id"],
                "slot": details["type"],
                "skin_type": "Armor",
                "weight_class": details["weight_class"],
            }
        ]


class TransformCsvSkinArmorDyeSlot(TransformCsvSkinTask):
    def get_rows(self, skin):
        skin_id = skin["id"]
        if skin["type"] != "Armor":
            return []
        details = skin["details"]
        dye_slots: dict = details.get("dye_slots", {})
        default_dye_slots: list[dict | None] = dye_slots.get("default", [])
        return [
            {
                "color_id": dye_slot["color_id"],
                "material": dye_slot["material"],
                "skin_id": skin_id,
                "slot_index": i,
            }
            for i, dye_slot in enumerate(default_dye_slots)
            if dye_slot is not None
        ]


class TransformCsvSkinBack(TransformCsvSkinTask):
    def get_rows(self, skin):
        if skin["type"] != "Back":
            return []
        return [{"skin_id": skin["id"], "skin_type": "Back"}]


class TransformCsvSkinDescription(TransformCsvSkinTask):
    def get_rows(self, skin):
        skin_description = skin.get("description")
        if skin_description is None or skin_description == "":
            return []
        return [
            {
                "app_name": "gw2",
                "lang_tag": self.lang_tag.value,
                "original": common.to_xhmtl_fragment(skin_description),
                "skin_id": skin["id"],
            }
        ]


class TransformCsvSkinFlag(TransformCsvSkinTask):
    def get_rows(self, skin):
        skin_id = skin["id"]
        return [{"flag": flag, "skin_id": skin_id} for flag in skin["flags"]]


class TransformCsvSkinGathering(TransformCsvSkinTask):
    def get_rows(self, skin):
        if skin["type"] != "Gathering":
            return []
        return [
            {
                "skin_id": skin["id"],
                "skin_type": "Gathering",
                "tool": skin["details"]["type"],
            }
        ]


class TransformCsvSkinName(TransformCsvSkinTask):
    def get_rows(self, skin):
        skin_name = skin.get("name")
        if skin_name is None or skin_name == "":
            return []
        return [
            {
                "app_name": "gw2",
                "lang_tag": self.lang_tag.value,
                "original": common.to_xhmtl_fragment(skin_name),
                "skin_id": skin["id"],
            }
        ]


class TransformCsvSkinRestriction(TransformCsvSkinTask):
    def get_rows(self, skin):
        skin_id = skin["id"]
        return [
            {"restriction": restriction, "skin_id": skin_id}
            for restriction in skin["restrictions"]
        ]


class TransformCsvSkinType(TransformCsvSkinTask):
    def get_rows(self, skin):
        return [{"skin_id": skin["id"], "skin_type": skin["type"]}]


class TransformCsvSkinWeapon(TransformCsvSkinTask):
    def get_rows(self, skin):
        if skin["type"] != "Weapon":
            return []
        details = skin["details"]
        return [
            {
                "damage_type": details["damage_type"],
                "skin_id": skin["id"],
                "skin_type": "Weapon",
                "weapon_type": details["type"],
            }
        ]
