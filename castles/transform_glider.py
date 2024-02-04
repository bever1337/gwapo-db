import enum
import luigi
from os import path

import common
import config
import extract_batch
import transform_csv
import transform_lang


class GliderTable(enum.Enum):
    Glider = "glider"
    GliderDescription = "glider_description"
    GliderDyeSlot = "glider_dye_slot"
    GliderName = "glider_name"


class TransformGlider(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    table = luigi.EnumParameter(enum=GliderTable)

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
            json_schema_path="./schema/gw2/v2/gliders/index.json",
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/gliders",
        )

    def get_rows(self, glider):
        glider_id = glider["id"]
        match self.table:
            case GliderTable.Glider:
                return [
                    {
                        "glider_id": glider_id,
                        "icon": glider["icon"],
                        "presentation_order": glider["order"],
                    }
                ]
            case GliderTable.GliderDescription:
                glider_description = glider["description"]
                if glider_description == "":
                    return []
                return [
                    {
                        "app_name": "gw2",
                        "glider_id": glider_id,
                        "lang_tag": self.lang_tag.value,
                        "original": transform_lang.to_xhmtl_fragment(
                            glider_description
                        ),
                    }
                ]
            case GliderTable.GliderDyeSlot:
                return [
                    {
                        "color_id": color_id,
                        "glider_id": glider_id,
                        "slot_index": index,
                    }
                    for index, color_id in enumerate(glider["default_dyes"])
                ]
            case GliderTable.GliderName:
                return [
                    {
                        "app_name": "gw2",
                        "glider_id": glider_id,
                        "lang_tag": self.lang_tag.value,
                        "original": transform_lang.to_xhmtl_fragment(glider["name"]),
                    }
                ]
            case _:
                raise RuntimeError("Unexpected table name")
