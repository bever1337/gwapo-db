import luigi

import common
import extract_batch
import transform_csv
import transform_lang


class TransformMountSkinTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        return extract_batch.ExtractBatchTask(
            json_schema_path="./schema/gw2/v2/mounts/skins/index.json",
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/mounts/skins",
        )


class TransformMountSkin(TransformMountSkinTask):
    def get_rows(self, mount_skin):
        return [
            {
                "icon": mount_skin["icon"],
                "mount_id": mount_skin["mount"],
                "mount_skin_id": mount_skin["id"],
            }
        ]


class TransformMountSkinDyeSlot(TransformMountSkinTask):
    def get_rows(self, mount_skin):
        mount_skin_id = mount_skin["id"]
        return [
            {
                "color_id": dye_slot["color_id"],
                "material": dye_slot["material"],
                "mount_skin_id": mount_skin_id,
                "slot_index": slot_index,
            }
            for slot_index, dye_slot in enumerate(mount_skin["dye_slots"])
        ]


class TransformMountSkinName(TransformMountSkinTask):
    def get_rows(self, mount_skin):
        return [
            {
                "app_name": "gw2",
                "mount_skin_id": mount_skin["id"],
                "lang_tag": self.lang_tag.value,
                "original": transform_lang.to_xhmtl_fragment(mount_skin["name"]),
            }
        ]
