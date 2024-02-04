import enum
import luigi
from os import path

import common
import config
import extract_batch
import transform_csv
import transform_lang


class FinisherTable(enum.Enum):
    Finisher = "finisher"
    FinisherDetail = "finisher_detail"
    FinisherName = "finisher_name"


class TransformFinisher(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    table = luigi.EnumParameter(enum=FinisherTable)

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
            json_schema_path="./schema/gw2/v2/finishers/index.json",
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/finishers",
        )

    def get_rows(self, finisher):
        finisher_id = finisher["id"]
        match self.table:
            case FinisherTable.Finisher:
                return [
                    {
                        "finisher_id": finisher_id,
                        "icon": finisher["icon"],
                        "presentation_order": finisher["order"],
                    }
                ]
            case FinisherTable.FinisherDetail:
                unlock_details = finisher["unlock_details"]
                if unlock_details == "":
                    return []
                return [
                    {
                        "app_name": "gw2",
                        "finisher_id": finisher_id,
                        "lang_tag": self.lang_tag.value,
                        "original": transform_lang.to_xhmtl_fragment(unlock_details),
                    }
                ]

            case FinisherTable.FinisherName:
                return [
                    {
                        "app_name": "gw2",
                        "finisher_id": finisher_id,
                        "lang_tag": self.lang_tag.value,
                        "original": transform_lang.to_xhmtl_fragment(finisher["name"]),
                    }
                ]
            case _:
                raise RuntimeError("Unexpected table name")
