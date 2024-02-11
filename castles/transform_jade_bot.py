import luigi

import common
import extract_batch
import transform_csv
import transform_lang


class TransformJadeBotTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        return extract_batch.ExtractBatchTask(
            json_schema_path="./schema/gw2/v2/jadebots/index.json",
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/jadebots",
        )


class TransformJadeBot(TransformJadeBotTask):
    def get_rows(self, jade_bot):
        return [{"jade_bot_id": jade_bot["id"]}]


class TransformJadeBotDescription(TransformJadeBotTask):
    def get_rows(self, jade_bot):
        return [
            {
                "app_name": "gw2",
                "jade_bot_id": jade_bot["id"],
                "lang_tag": self.lang_tag.value,
                "original": transform_lang.to_xhmtl_fragment(jade_bot["description"]),
            }
        ]


class TransformJadeBotItem(TransformJadeBotTask):
    def get_rows(self, jade_bot):
        return [{"jade_bot_id": jade_bot["id"], "item_id": jade_bot["unlock_item"]}]


class TransformJadeBotName(TransformJadeBotTask):
    def get_rows(self, jade_bot):
        return [
            {
                "app_name": "gw2",
                "jade_bot_id": jade_bot["id"],
                "lang_tag": self.lang_tag.value,
                "original": transform_lang.to_xhmtl_fragment(jade_bot["name"]),
            }
        ]
