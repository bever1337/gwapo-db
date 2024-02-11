import luigi

import common
import extract_batch
import transform_csv
import transform_lang


class TransformOutfitTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        return extract_batch.ExtractBatchTask(
            json_schema_path="./schema/gw2/v2/outfits/index.json",
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/outfits",
        )


class TransformOutfit(TransformOutfitTask):
    def get_rows(self, outfit):
        return [{"icon": outfit["icon"], "outfit_id": outfit["id"]}]


class TransformOutfitItem(TransformOutfitTask):
    def get_rows(self, outfit):
        outfit_id = outfit["id"]
        return [
            {"item_id": item_id, "outfit_id": outfit_id}
            for item_id in outfit["unlock_items"]
        ]


class TransformOutfitName(TransformOutfitTask):
    def get_rows(self, outfit):
        return [
            {
                "app_name": "gw2",
                "outfit_id": outfit["id"],
                "lang_tag": self.lang_tag.value,
                "original": transform_lang.to_xhmtl_fragment(outfit["name"]),
            }
        ]
