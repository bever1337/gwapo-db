import enum
import luigi
from os import path

import common
import config
import extract_batch
import transform_csv
import transform_lang


class NoveltyTable(enum.Enum):
    Novelty = "novelty"
    NoveltyDescription = "novelty_description"
    NoveltyItem = "novelty_item"
    NoveltyName = "novelty_name"


class TransformNovelty(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    table = luigi.EnumParameter(enum=NoveltyTable)

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
            json_schema_path="./schema/gw2/v2/novelties/index.json",
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
                        "original": transform_lang.to_xhmtl_fragment(
                            novelty_description
                        ),
                    }
                ]
            case NoveltyTable.NoveltyItem:
                return [
                    {"item_id": item_id, "novelty_id": novelty_id}
                    for item_id in novelty["unlock_item"]
                ]
            case NoveltyTable.NoveltyName:
                return [
                    {
                        "app_name": "gw2",
                        "lang_tag": self.lang_tag.value,
                        "novelty_id": novelty_id,
                        "original": transform_lang.to_xhmtl_fragment(novelty["name"]),
                    }
                ]
            case _:
                raise RuntimeError("Unexpected table name")
