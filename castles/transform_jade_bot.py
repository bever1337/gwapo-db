import enum
import luigi
from os import path

import common
import config
import extract_batch
import transform_csv
import transform_lang


class JadeBotTable(enum.Enum):
    JadeBot = "jade_bot"
    JadeBotDescription = "jade_bot_description"
    JadeBotName = "jade_bot_name"


class TransformJadeBot(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    table = luigi.EnumParameter(enum=JadeBotTable)

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
            json_schema_path="./schema/gw2/v2/jadebots/index.json",
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/jadebots",
        )

    def get_rows(self, jade_bot):
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
                        "original": transform_lang.to_xhmtl_fragment(
                            jade_bot["description"]
                        ),
                    }
                ]
            case JadeBotTable.JadeBotName:
                return [
                    {
                        "app_name": "gw2",
                        "jade_bot_id": jade_bot_id,
                        "lang_tag": self.lang_tag.value,
                        "original": transform_lang.to_xhmtl_fragment(jade_bot["name"]),
                    }
                ]
            case _:
                raise RuntimeError("Unexpected table name")
