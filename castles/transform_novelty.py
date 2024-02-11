import luigi

import common
import extract_batch
import transform_csv
import transform_lang


class TransformNoveltyTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        return extract_batch.ExtractBatchTask(
            json_schema_path="./schema/gw2/v2/novelties/index.json",
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/novelties",
        )


class TransformNovelty(TransformNoveltyTask):
    def get_rows(self, novelty):
        return [
            {
                "icon": novelty["icon"],
                "novelty_id": novelty["id"],
                "slot": novelty["slot"],
            }
        ]


class TransformNoveltyDescription(TransformNoveltyTask):
    def get_rows(self, novelty):
        novelty_description = novelty["description"]
        if novelty_description == "":
            return []
        return [
            {
                "app_name": "gw2",
                "lang_tag": self.lang_tag.value,
                "novelty_id": novelty["id"],
                "original": transform_lang.to_xhmtl_fragment(novelty_description),
            }
        ]


class TransformNoveltyItem(TransformNoveltyTask):
    def get_rows(self, novelty):
        novelty_id = novelty["id"]
        return [
            {"item_id": item_id, "novelty_id": novelty_id}
            for item_id in novelty["unlock_item"]
        ]


class TransformNoveltyName(TransformNoveltyTask):
    def get_rows(self, novelty):
        return [
            {
                "app_name": "gw2",
                "lang_tag": self.lang_tag.value,
                "novelty_id": novelty["id"],
                "original": transform_lang.to_xhmtl_fragment(novelty["name"]),
            }
        ]
