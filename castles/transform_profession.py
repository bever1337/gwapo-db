import luigi

import common
import extract_batch
import transform_csv
import transform_lang


class TransformProfessionTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        return extract_batch.ExtractBatchTask(
            json_schema_path="./schema/gw2/v2/professions/index.json",
            url_params={"lang": self.lang_tag.value, "v": "2019-12-19T00:00:00.000Z"},
            url="https://api.guildwars2.com/v2/professions",
        )


class TransformProfession(TransformProfessionTask):
    def get_rows(self, profession):
        return [
            {
                "code": profession["code"],
                "icon_big": profession["icon_big"],
                "icon": profession["icon"],
                "profession_id": profession["id"],
            }
        ]


class TransformProfessionName(TransformProfessionTask):
    def get_rows(self, profession):
        return [
            {
                "app_name": "gw2",
                "profession_id": profession["id"],
                "lang_tag": self.lang_tag.value,
                "original": transform_lang.to_xhmtl_fragment(profession["name"]),
            }
        ]
