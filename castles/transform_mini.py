import enum
import luigi
from os import path

import common
import config
import extract_batch
import transform_csv
import transform_lang


class MiniTable(enum.Enum):
    Mini = "mini"
    MiniUnlock = "mini_unlock"
    MiniName = "mini_name"


class TransformMini(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    table = luigi.EnumParameter(enum=MiniTable)

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
            json_schema_path="./schema/gw2/v2/minis/index.json",
            json_patch_path="./patch/mini.json",
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
                        "original": transform_lang.to_xhmtl_fragment(mini["name"]),
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
                        "original": transform_lang.to_xhmtl_fragment(mini_unlock),
                    }
                ]
            case _:
                raise RuntimeError("Unexpected table name")
