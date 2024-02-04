import datetime
import enum
import luigi
from os import path

import common
import extract_batch
import transform_csv


class RaceTable(enum.Enum):
    Race = "race"
    RaceName = "race_name"


class TransformRace(transform_csv.TransformCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True)
    table = luigi.EnumParameter(enum=RaceTable)

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
            json_schema_path="./schema/gw2/v2/races/index.json",
            output_dir=self.output_dir,
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/races",
        )

    def get_rows(self, race):
        race_id = race["id"]
        match self.table:
            case RaceTable.Race:
                return [{"race_id": race_id}]
            case RaceTable.RaceName:
                return [
                    {
                        "app_name": "gw2",
                        "lang_tag": self.lang_tag.value,
                        "original": race["name"],
                        "race_id": race_id,
                    }
                ]
            case _:
                raise RuntimeError("Unexpected table name")
