import datetime
import enum
import luigi
from os import path

import common
import config
import extract_batch
import transform_csv


class SpecializationTable(enum.Enum):
    Specialization = "specialization"
    SpecializationName = "specialization_name"


class TransformSpecialization(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    table = luigi.EnumParameter(enum=SpecializationTable)

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
            json_schema_path="./schema/gw2/v2/specializations/index.json",
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/specializations",
        )

    def get_rows(self, specialization):
        specialization_id = specialization["id"]

        match self.table:
            case SpecializationTable.Specialization:
                return [
                    {
                        "background": specialization["background"],
                        "elite": specialization["elite"],
                        "icon": specialization["icon"],
                        "profession_id": specialization["profession"],
                        "specialization_id": specialization_id,
                    }
                ]
            case SpecializationTable.SpecializationName:
                return [
                    {
                        "app_name": "gw2",
                        "specialization_id": specialization_id,
                        "lang_tag": self.lang_tag.value,
                        "original": specialization["name"],
                    }
                ]
            case _:
                raise RuntimeError("Unexpected table name")
