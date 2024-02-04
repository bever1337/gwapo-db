import datetime
import enum
import luigi
from os import path

import common
import config
import extract_batch
import transform_csv


class OutfitTable(enum.Enum):
    Outfit = "outfit"
    OutfitName = "outfit_name"


class TransformOutfit(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    table = luigi.EnumParameter(enum=OutfitTable)

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
            json_schema_path="./schema/gw2/v2/outfits/index.json",
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/outfits",
        )

    def get_rows(self, outfit):
        outfit_id = outfit["id"]

        match self.table:
            case OutfitTable.Outfit:
                return [{"icon": outfit["icon"], "outfit_id": outfit_id}]
            case OutfitTable.OutfitName:
                return [
                    {
                        "app_name": "gw2",
                        "outfit_id": outfit_id,
                        "lang_tag": self.lang_tag.value,
                        "original": outfit["name"],
                    }
                ]
            case _:
                raise RuntimeError("Unexpected table name")
