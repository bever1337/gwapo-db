import datetime
import enum
import luigi
from os import path

import common
import extract_batch
import transform_csv


class ProfessionTable(enum.Enum):
    Profession = "profession"
    ProfessionName = "profession_name"


class TransformProfession(transform_csv.TransformCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True)
    table = luigi.EnumParameter(enum=ProfessionTable)

    def output(self):
        output_folder_name = "_".join(["transform", self.table.value])
        return common.from_output_params(
            output_dir=path.join(self.output_dir, output_folder_name),
            extract_datetime=self.extract_datetime,
            params={"lang": self.lang_tag.value, "v": "2019-12-19T00:00:00.000Z"},
            ext="csv",
        )

    def requires(self):
        return extract_batch.ExtractBatchTask(
            extract_datetime=self.extract_datetime,
            json_schema_path="./schema/gw2/v2/professions/index.json",
            output_dir=self.output_dir,
            url_params={"lang": self.lang_tag.value, "v": "2019-12-19T00:00:00.000Z"},
            url="https://api.guildwars2.com/v2/professions",
        )

    def get_rows(self, profession):
        profession_id = profession["id"]

        match self.table:
            case ProfessionTable.Profession:
                return [
                    {
                        "code": profession["code"],
                        "icon_big": profession["icon_big"],
                        "icon": profession["icon"],
                        "profession_id": profession_id,
                    }
                ]
            case ProfessionTable.ProfessionName:
                return [
                    {
                        "app_name": "gw2",
                        "profession_id": profession_id,
                        "lang_tag": self.lang_tag.value,
                        "original": profession["name"],
                    }
                ]
            case _:
                raise RuntimeError("Unexpected table name")
