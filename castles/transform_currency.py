import enum
import luigi
from os import path

import common
import config
import transform_csv
import transform_lang
import transform_patch_currency


class CurrencyTable(enum.Enum):
    Currency = "currency"
    CurrencyCategory = "currency_category"
    CurrencyDescription = "currency_description"
    CurrencyName = "currency_name"


class TransformCurrency(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    table = luigi.EnumParameter(enum=CurrencyTable)

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
        return transform_patch_currency.TransformPatchCurrency(lang_tag=self.lang_tag)

    def get_rows(self, currency):
        match self.table:
            case CurrencyTable.Currency:
                return [
                    {
                        "currency_id": currency["id"],
                        "deprecated": currency["deprecated"],
                        "icon": currency["icon"],
                        "presentation_order": currency["order"],
                    }
                ]
            case CurrencyTable.CurrencyCategory:
                return [
                    {"category": category, "currency_id": currency["id"]}
                    for category in currency["categories"]
                ]
            case CurrencyTable.CurrencyDescription:
                return [
                    {
                        "app_name": "gw2",
                        "currency_id": currency["id"],
                        "lang_tag": self.lang_tag.value,
                        "original": transform_lang.to_xhmtl_fragment(
                            currency["description"]
                        ),
                    }
                ]
            case CurrencyTable.CurrencyName:
                return [
                    {
                        "app_name": "gw2",
                        "currency_id": currency["id"],
                        "lang_tag": self.lang_tag.value,
                        "original": transform_lang.to_xhmtl_fragment(currency["name"]),
                    }
                ]
            case _:
                raise RuntimeError("Unexpected table name")
