import luigi

import common
import extract_batch
import transform_csv
import transform_lang


class TransformSpecializationTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        return extract_batch.ExtractBatchTask(
            json_schema_path="./schema/gw2/v2/specializations/index.json",
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/specializations",
        )


class TransformSpecialization(TransformSpecializationTask):
    def get_rows(self, specialization):
        return [
            {
                "background": specialization["background"],
                "elite": specialization["elite"],
                "icon": specialization["icon"],
                "profession_id": specialization["profession"],
                "specialization_id": specialization["id"],
            }
        ]


class TransformSpecializationName(TransformSpecializationTask):
    def get_rows(self, specialization):
        return [
            {
                "app_name": "gw2",
                "specialization_id": specialization["id"],
                "lang_tag": self.lang_tag.value,
                "original": transform_lang.to_xhmtl_fragment(specialization["name"]),
            }
        ]
