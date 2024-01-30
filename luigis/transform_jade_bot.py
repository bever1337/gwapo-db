import datetime
import enum
import luigi
from os import path

import common
import extract_batch
import transform_csv


class JadeBotTable(enum.Enum):
    JadeBot = "jade_bot"
    JadeBotDescription = "jade_bot_description"
    JadeBotName = "jade_bot_name"


class TransformJadeBot(transform_csv.TransformCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True)
    table = luigi.EnumParameter(enum=JadeBotTable)

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
            json_schema_path="./schema/gw2/v2/jadebots/index.json",
            output_dir=self.output_dir,
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/jadebots",
        )

    def run(self, jade_bot):
        jade_bot_id = jade_bot["id"]
        match self.table:
            case JadeBotTable.JadeBot:
                return [{"jade_bot_id": jade_bot_id}]
            case JadeBotTable.JadeBotDescription:
                return [
                    {
                        "app_name": "gw2",
                        "jade_bot_id": jade_bot_id,
                        "lang_tag": self.lang_tag.value,
                        "original": jade_bot["description"],
                    }
                ]
            case JadeBotTable.JadeBotName:
                return [
                    {
                        "app_name": "gw2",
                        "jade_bot_id": jade_bot_id,
                        "lang_tag": self.lang_tag.value,
                        "original": jade_bot["name"],
                    }
                ]
            case _:
                raise RuntimeError("Unexpected table name")
