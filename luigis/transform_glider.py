import datetime
import enum
import luigi
from os import path

import common
import extract_batch
import transform_csv


class GliderTable(enum.Enum):
    Glider = "glider"
    GliderDescription = "glider_description"
    GliderDyeSlot = "glider_dye_slot"
    GliderName = "glider_name"


class TransformGlider(transform_csv.TransformCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True)
    table = luigi.EnumParameter(enum=GliderTable)

    def output(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.csv".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        target_dir = "_".join(["transform", self.table.value])
        target_path = path.join(
            self.output_dir,
            target_dir,
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        return extract_batch.ExtractBatchTask(
            extract_datetime=self.extract_datetime,
            json_schema_path="./schema/gw2/v2/gliders/index.json",
            output_dir=self.output_dir,
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/gliders",
        )

    def run(self, glider):
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
                return [
                    {
                        "app_name": "gw2",
                        "glider_id": glider_id,
                        "lang_tag": self.lang_tag.value,
                        "original": glider["description"],
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
                        "original": glider["name"],
                    }
                ]
            case _:
                raise RuntimeError("Unexpected table name")
