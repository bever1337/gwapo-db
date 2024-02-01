import datetime
import enum
import luigi
from os import path

import common
import extract_batch
import transform_csv


class SkiffTable(enum.Enum):
    Skiff = "skiff"
    SkiffDyeSlot = "skiff_dye_slot"
    SkiffName = "skiff_name"


class TransformSkiff(transform_csv.TransformCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True)
    table = luigi.EnumParameter(enum=SkiffTable)

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
            json_schema_path="./schema/gw2/v2/skiffs/index.json",
            output_dir=self.output_dir,
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/skiffs",
        )

    def get_rows(self, skiff):
        skiff_id = skiff["id"]

        match self.table:
            case SkiffTable.Skiff:
                return [{"icon": skiff["icon"], "skiff_id": skiff_id}]
            case SkiffTable.SkiffDyeSlot:
                return [
                    {
                        "color_id": dye_slot["color_id"],
                        "material": dye_slot["material"],
                        "skiff_id": skiff_id,
                        "slot_index": slot_index,
                    }
                    for slot_index, dye_slot in enumerate(skiff["dye_slots"])
                ]
            case SkiffTable.SkiffName:
                return [
                    {
                        "app_name": "gw2",
                        "lang_tag": self.lang_tag.value,
                        "original": skiff["name"],
                        "skiff_id": skiff_id,
                    }
                ]
            case _:
                raise RuntimeError("Unexpected table name")
