import datetime
import luigi

import common
from tasks import transform_csv
import currency_transform_patch


class TransformCsvCurrencyTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "currency"

    def requires(self):
        return currency_transform_patch.TransformPatch(lang_tag=self.lang_tag)


class TransformCsvCurrency(TransformCsvCurrencyTask):
    def get_rows(self, currency):
        return [
            {
                "currency_id": currency["id"],
                "deprecated": currency["deprecated"],
                "icon": currency["icon"],
                "presentation_order": currency["order"],
            }
        ]


class TransformCsvCurrencyCategory(TransformCsvCurrencyTask):
    def get_rows(self, currency):
        return [
            {"category": category, "currency_id": currency["id"]}
            for category in currency["categories"]
        ]


class TransformCsvCurrencyDescription(TransformCsvCurrencyTask):
    def get_rows(self, currency):
        return [
            {
                "app_name": "gw2",
                "currency_id": currency["id"],
                "lang_tag": self.lang_tag.value,
                "original": common.to_xhmtl_fragment(currency["description"]),
            }
        ]


class TransformCsvCurrencyName(TransformCsvCurrencyTask):
    def get_rows(self, currency):
        return [
            {
                "app_name": "gw2",
                "currency_id": currency["id"],
                "lang_tag": self.lang_tag.value,
                "original": common.to_xhmtl_fragment(currency["name"]),
            }
        ]
