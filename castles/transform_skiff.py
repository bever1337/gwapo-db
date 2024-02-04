import enum
import luigi
from os import path

import common
import config
import extract_batch
import transform_csv
import transform_lang


class SkiffTable(enum.Enum):
    Skiff = "skiff"
    SkiffDyeSlot = "skiff_dye_slot"
    SkiffName = "skiff_name"


class TransformSkiff(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    table = luigi.EnumParameter(enum=SkiffTable)

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
            json_schema_path="./schema/gw2/v2/skiffs/index.json",
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
                        "original": transform_lang.to_xhmtl_fragment(skiff["name"]),
                        "skiff_id": skiff_id,
                    }
                ]
            case _:
                raise RuntimeError("Unexpected table name")
