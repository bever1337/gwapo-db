import datetime
import enum
import luigi
from os import path

import common
import config
import extract_batch
import transform_csv


class MountSkinTable(enum.Enum):
    MountSkin = "mount_skin"
    MountSkinDyeSlot = "mount_skin_dye_slot"
    MountSkinName = "mount_skin_name"


class TransformMountSkin(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    table = luigi.EnumParameter(enum=MountSkinTable)

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
            json_schema_path="./schema/gw2/v2/mounts/skins/index.json",
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/mounts/skins",
        )

    def get_rows(self, mount_skin):
        mount_skin_id = mount_skin["id"]

        match self.table:
            case MountSkinTable.MountSkin:
                return [
                    {
                        "icon": mount_skin["icon"],
                        "mount_id": mount_skin["mount"],
                        "mount_skin_id": mount_skin_id,
                    }
                ]
            case MountSkinTable.MountSkinDyeSlot:
                return [
                    {
                        "color_id": dye_slot["color_id"],
                        "material": dye_slot["material"],
                        "mount_skin_id": mount_skin_id,
                        "slot_index": slot_index,
                    }
                    for slot_index, dye_slot in enumerate(mount_skin["dye_slots"])
                ]
            case MountSkinTable.MountSkinName:
                return [
                    {
                        "app_name": "gw2",
                        "mount_skin_id": mount_skin_id,
                        "lang_tag": self.lang_tag.value,
                        "original": mount_skin["name"],
                    }
                ]
            case _:
                raise RuntimeError("Unexpected table name")
