import datetime
import enum
import luigi
from os import path

import common
import extract_batch
import transform_csv


class FinisherTable(enum.Enum):
    Finisher = "finisher"
    FinisherDetail = "finisher_detail"
    FinisherName = "finisher_name"


class TransformFinisher(transform_csv.TransformCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True)
    table = luigi.EnumParameter(enum=FinisherTable)

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
            json_schema_path="./schema/gw2/v2/finishers/index.json",
            output_dir=self.output_dir,
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
                return [
                    {
                        "app_name": "gw2",
                        "finisher_id": finisher_id,
                        "lang_tag": self.lang_tag.value,
                        "original": finisher["unlock_details"],
                    }
                ]

            case FinisherTable.FinisherName:
                return [
                    {
                        "app_name": "gw2",
                        "finisher_id": finisher_id,
                        "lang_tag": self.lang_tag.value,
                        "original": finisher["name"],
                    }
                ]
            case _:
                raise RuntimeError("Unexpected table name")
