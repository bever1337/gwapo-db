import datetime
import enum
import luigi
from os import path

import common
import extract_batch
import transform_csv


class NoveltyTable(enum.Enum):
    Novelty = "novelty"
    NoveltyDescription = "novelty_description"
    NoveltyName = "novelty_name"


class TransformNovelty(transform_csv.TransformCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True)
    table = luigi.EnumParameter(enum=NoveltyTable)

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
            json_schema_path="./schema/gw2/v2/novelties/index.json",
            output_dir=self.output_dir,
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/novelties",
        )

    def get_rows(self, novelty):
        novelty_id = novelty["id"]
        match self.table:
            case NoveltyTable.Novelty:
                return [
                    {
                        "icon": novelty["icon"],
                        "novelty_id": novelty_id,
                        "slot": novelty["slot"],
                    }
                ]
            case NoveltyTable.NoveltyDescription:
                novelty_description = novelty["description"]
                if novelty_description == "":
                    return []
                return [
                    {
                        "app_name": "gw2",
                        "lang_tag": self.lang_tag.value,
                        "novelty_id": novelty_id,
                        "original": novelty_description,
                    }
                ]
            case NoveltyTable.NoveltyName:
                return [
                    {
                        "app_name": "gw2",
                        "lang_tag": self.lang_tag.value,
                        "novelty_id": novelty_id,
                        "original": novelty["name"],
                    }
                ]
            case _:
                raise RuntimeError("Unexpected table name")
