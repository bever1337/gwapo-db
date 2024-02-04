import enum
import luigi
from os import path

import common
import config
import extract_batch
import transform_csv
import transform_lang


class ProfessionTable(enum.Enum):
    Profession = "profession"
    ProfessionName = "profession_name"


class TransformProfession(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    table = luigi.EnumParameter(enum=ProfessionTable)

    def output(self):
        gwapo_config = config.gconfig()
        output_folder_name = "_".join(["transform", self.table.value])
        return common.from_output_params(
            output_dir=path.join(gwapo_config.output_dir, output_folder_name),
            extract_datetime=gwapo_config.extract_datetime,
            params={"lang": self.lang_tag.value, "v": "2019-12-19T00:00:00.000Z"},
            ext="csv",
        )

    def requires(self):
        return extract_batch.ExtractBatchTask(
            json_schema_path="./schema/gw2/v2/professions/index.json",
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
                        "original": transform_lang.to_xhmtl_fragment(
                            profession["name"]
                        ),
                    }
                ]
            case _:
                raise RuntimeError("Unexpected table name")
