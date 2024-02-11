import luigi

import common
import transform_csv
import transform_lang
import transform_patch_currency


class TransformCurrencyTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        return transform_patch_currency.TransformPatchCurrency(lang_tag=self.lang_tag)


class TransformCurrency(TransformCurrencyTask):
    def get_rows(self, currency):
        return [
            {
                "currency_id": currency["id"],
                "deprecated": currency["deprecated"],
                "icon": currency["icon"],
                "presentation_order": currency["order"],
            }
        ]


class TransformCurrencyCategory(TransformCurrencyTask):
    def get_rows(self, currency):
        return [
            {"category": category, "currency_id": currency["id"]}
            for category in currency["categories"]
        ]


class TransformCurrencyDescription(TransformCurrencyTask):
    def get_rows(self, currency):
        return [
            {
                "app_name": "gw2",
                "currency_id": currency["id"],
                "lang_tag": self.lang_tag.value,
                "original": transform_lang.to_xhmtl_fragment(currency["description"]),
            }
        ]


class TransformCurrencyName(TransformCurrencyTask):
    def get_rows(self, currency):
        return [
            {
                "app_name": "gw2",
                "currency_id": currency["id"],
                "lang_tag": self.lang_tag.value,
                "original": transform_lang.to_xhmtl_fragment(currency["name"]),
            }
        ]
