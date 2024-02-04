import datetime
import enum
import luigi
from os import path

import common
import extract_batch
import transform_csv


class MountTable(enum.Enum):
    Mount = "mount"
    MountName = "mount_name"


class TransformMount(transform_csv.TransformCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True)
    table = luigi.EnumParameter(enum=MountTable)

    def output(self):
        output_folder_name = "_".join(["transform", self.table.value])
        return common.from_output_params(
            output_dir=path.join(self.output_dir, output_folder_name),
            extract_datetime=self.extract_datetime,
            params={"lang": self.lang_tag.value},
            ext="csv",
        )

    def requires(self):
        return extract_batch.ExtractBatchTask(
            extract_datetime=self.extract_datetime,
            json_schema_path="./schema/gw2/v2/mounts/types/index.json",
            output_dir=self.output_dir,
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/mounts/types",
        )

    def get_rows(self, mount):
        mount_id = mount["id"]

        match self.table:
            case MountTable.Mount:
                return [{"mount_id": mount_id}]
            case MountTable.MountName:
                return [
                    {
                        "app_name": "gw2",
                        "mount_id": mount_id,
                        "lang_tag": self.lang_tag.value,
                        "original": mount["name"],
                    }
                ]
            case _:
                raise RuntimeError("Unexpected table name")
