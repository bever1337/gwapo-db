import datetime
import enum
import luigi
from os import path

import common
import extract_batch
import transform_csv


class MiniTable(enum.Enum):
    Mini = "mini"
    MiniUnlock = "mini_unlock"
    MiniName = "mini_name"


class TransformMini(transform_csv.TransformCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True)
    table = luigi.EnumParameter(enum=MiniTable)

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
            json_schema_path="./schema/gw2/v2/minis/index.json",
            json_patch_path="./patch/mini.json",
            output_dir=self.output_dir,
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/minis",
        )

    def get_rows(self, mini):
        mini_id = mini["id"]
        match self.table:
            case MiniTable.Mini:
                return [
                    {
                        "icon": mini["icon"],
                        "mini_id": mini_id,
                        "presentation_order": mini["order"],
                    }
                ]
            case MiniTable.MiniName:
                return [
                    {
                        "app_name": "gw2",
                        "lang_tag": self.lang_tag.value,
                        "mini_id": mini_id,
                        "original": mini["name"],
                    }
                ]
            case MiniTable.MiniUnlock:
                mini_unlock = mini.get("unlock")
                if mini_unlock == None:
                    return []
                return [
                    {
                        "app_name": "gw2",
                        "lang_tag": self.lang_tag.value,
                        "mini_id": mini_id,
                        "original": mini["description"],
                    }
                ]
            case _:
                raise RuntimeError("Unexpected table name")
