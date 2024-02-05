import enum
import luigi
from os import path

import common
import config
import extract_batch
import transform_csv
import transform_lang


class MountTable(enum.Enum):
    Mount = "mount"
    MountSkinDefault = "mount_skin_default"
    MountName = "mount_name"


class TransformMount(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    table = luigi.EnumParameter(enum=MountTable)

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
            json_schema_path="./schema/gw2/v2/mounts/types/index.json",
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/mounts/types",
        )

    def get_rows(self, mount):
        mount_id = mount["id"]

        match self.table:
            case MountTable.Mount:
                return [{"mount_id": mount_id}]
            case MountTable.MountSkinDefault:
                return [{"mount_id": mount_id, "mount_skin_id": mount["default_skin"]}]
            case MountTable.MountName:
                return [
                    {
                        "app_name": "gw2",
                        "mount_id": mount_id,
                        "lang_tag": self.lang_tag.value,
                        "original": transform_lang.to_xhmtl_fragment(mount["name"]),
                    }
                ]
            case _:
                raise RuntimeError("Unexpected table name")
