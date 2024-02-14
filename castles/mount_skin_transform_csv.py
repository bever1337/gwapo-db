import datetime
import luigi

import common
import mount_skin_extract
from tasks import transform_csv


class TransformCsvMountSkinTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "mount_skin"

    def requires(self):
        return mount_skin_extract.ExtractBatch(lang_tag=self.lang_tag)


class TransformCsvMountSkin(TransformCsvMountSkinTask):
    def get_rows(self, mount_skin):
        return [
            {
                "icon": mount_skin["icon"],
                "mount_id": mount_skin["mount"],
                "mount_skin_id": mount_skin["id"],
            }
        ]


class TransformCsvMountSkinDyeSlot(TransformCsvMountSkinTask):
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


class TransformCsvMountSkinName(TransformCsvMountSkinTask):
    def get_rows(self, mount_skin):
        return [
            {
                "app_name": "gw2",
                "mount_skin_id": mount_skin["id"],
                "lang_tag": self.lang_tag.value,
                "original": common.to_xhmtl_fragment(mount_skin["name"]),
            }
        ]
