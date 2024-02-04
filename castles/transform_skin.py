import enum
import luigi
from os import path

import common
import config
import extract_batch
import transform_csv
import transform_lang


class SkinTable(enum.Enum):
    Skin = "skin"
    SkinArmor = "skin_armor"
    SkinArmorDyeSlot = "skin_armor_dye_slot"
    SkinBack = "skin_back"
    SkinDescription = "skin_description"
    SkinFlag = "skin_flag"
    SkinGathering = "skin_gathering"
    SkinName = "skin_name"
    SkinRestriction = "skin_restriction"
    SkinType = "skin_type"
    SkinWeapon = "skin_weapon"


class TransformSkin(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    table = luigi.EnumParameter(enum=SkinTable)

    def output(self):
        gwapo_config = config.gconfig()
        output_folder_name = "_".join(["transform", self.table.value])
        return common.from_output_params(
            output_dir=path.join(gwapo_config.output_dir, output_folder_name),
            extract_datetime=gwapo_config.extract_datetime,
            params={"lang": self.lang_tag.value},
            ext="csv",
        )

    def requires(self):
        return extract_batch.ExtractBatchTask(
            json_schema_path="./schema/gw2/v2/skins/index.json",
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/skins",
        )

    def get_rows(self, skin):
        skin_id = skin["id"]
        match self.table:
            case SkinTable.Skin:
                skin_icon = skin.get("icon")
                if skin_icon == "":
                    skin_icon = None
                return [
                    {"icon": skin_icon, "rarity": skin["rarity"], "skin_id": skin_id}
                ]
            case SkinTable.SkinArmor:
                if skin["type"] != "Armor":
                    return []
                details = skin["details"]
                return [
                    {
                        "skin_id": skin_id,
                        "slot": details["type"],
                        "skin_type": "Armor",
                        "weight_class": details["weight_class"],
                    }
                ]
            case SkinTable.SkinArmorDyeSlot:
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
            case SkinTable.SkinBack:
                if skin["type"] != "Back":
                    return []
                return [{"skin_id": skin_id, "skin_type": "Back"}]
            case SkinTable.SkinDescription:
                skin_description = skin.get("description")
                if skin_description is None or skin_description == "":
                    return []
                return [
                    {
                        "app_name": "gw2",
                        "lang_tag": self.lang_tag.value,
                        "original": transform_lang.to_xhmtl_fragment(skin_description),
                        "skin_id": skin_id,
                    }
                ]
            case SkinTable.SkinFlag:
                return [{"flag": flag, "skin_id": skin_id} for flag in skin["flags"]]
            case SkinTable.SkinGathering:
                if skin["type"] != "Gathering":
                    return []
                return [
                    {
                        "skin_id": skin_id,
                        "skin_type": "Gathering",
                        "tool": skin["details"]["type"],
                    }
                ]
            case SkinTable.SkinName:
                skin_name = skin.get("name")
                if skin_name is None or skin_name == "":
                    return []
                return [
                    {
                        "app_name": "gw2",
                        "lang_tag": self.lang_tag.value,
                        "original": transform_lang.to_xhmtl_fragment(skin_name),
                        "skin_id": skin_id,
                    }
                ]
            case SkinTable.SkinRestriction:
                return [
                    {"restriction": restriction, "skin_id": skin_id}
                    for restriction in skin["restrictions"]
                ]
            case SkinTable.SkinType:
                return [{"skin_id": skin_id, "skin_type": skin["type"]}]
            case SkinTable.SkinWeapon:
                if skin["type"] != "Weapon":
                    return []
                details = skin["details"]
                return [
                    {
                        "damage_type": details["damage_type"],
                        "skin_id": skin_id,
                        "skin_type": "Weapon",
                        "weapon_type": details["type"],
                    }
                ]
            case _:
                raise RuntimeError("Unexpected table name")
