import datetime
import enum
import luigi
from os import path

import common
import extract_batch
import transform_csv


class OutfitTable(enum.Enum):
    Outfit = "outfit"
    OutfitName = "outfit_name"


class TransformOutfit(transform_csv.TransformCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True)
    table = luigi.EnumParameter(enum=OutfitTable)

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
            json_schema_path="./schema/gw2/v2/outfits/index.json",
            output_dir=self.output_dir,
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
