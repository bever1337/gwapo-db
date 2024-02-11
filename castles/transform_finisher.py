import luigi

import common
import extract_batch
import transform_csv
import transform_lang


class TransformFinisherTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        return extract_batch.ExtractBatchTask(
            json_schema_path="./schema/gw2/v2/finishers/index.json",
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/finishers",
        )


class TransformFinisher(TransformFinisherTask):
    def get_rows(self, finisher):
        return [
            {
                "finisher_id": finisher["id"],
                "icon": finisher["icon"],
                "presentation_order": finisher["order"],
            }
        ]


class TransformFinisherDetail(TransformFinisherTask):
    def get_rows(self, finisher):
        unlock_details = finisher["unlock_details"]
        if unlock_details == "":
            return []
        return [
            {
                "app_name": "gw2",
                "finisher_id": finisher["id"],
                "lang_tag": self.lang_tag.value,
                "original": transform_lang.to_xhmtl_fragment(unlock_details),
            }
        ]


class TransformFinisherItem(TransformFinisherTask):
    def get_rows(self, finisher):
        finisher_id = finisher["id"]
        return [
            {"finisher_id": finisher_id, "item_id": item_id}
            for item_id in finisher["unlock_items"]
        ]


class TransformFinisherName(TransformFinisherTask):
    def get_rows(self, finisher):
        return [
            {
                "app_name": "gw2",
                "finisher_id": finisher["id"],
                "lang_tag": self.lang_tag.value,
                "original": transform_lang.to_xhmtl_fragment(finisher["name"]),
            }
        ]
