import luigi

import common
import currency_transform_patch
from tasks import config
from tasks import transform_csv


class TransformCsvCurrencyTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
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


class TransformCsvCurrencyDescriptionTranslation(transform_csv.TransformCsvTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "currency"
    translation_lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def get_rows(self, currency):
        return [
            {
                "app_name": self.app_name,
                "currency_id": currency["id"],
                "original_lang_tag": self.original_lang_tag.value,
                "translation_lang_tag": self.translation_lang_tag.value,
                "translation": common.to_xhmtl_fragment(currency["description"]),
            }
        ]

    def requires(self):
        return currency_transform_patch.TransformPatch(
            lang_tag=self.translation_lang_tag
        )


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


class TransformCsvCurrencyNameTranslation(transform_csv.TransformCsvTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "currency"
    translation_lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def get_rows(self, currency):
        return [
            {
                "app_name": self.app_name,
                "currency_id": currency["id"],
                "original_lang_tag": self.original_lang_tag.value,
                "translation_lang_tag": self.translation_lang_tag.value,
                "translation": common.to_xhmtl_fragment(currency["name"]),
            }
        ]

    def requires(self):
        return currency_transform_patch.TransformPatch(
            lang_tag=self.translation_lang_tag
        )
