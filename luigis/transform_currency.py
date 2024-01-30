import datetime
import enum
import luigi
from os import path

import common
import extract_batch
import transform_csv


class CurrencyTable(enum.Enum):
    Currency = "currency"
    CurrencyCategory = "currency_category"
    CurrencyDescription = "currency_description"
    CurrencyName = "currency_name"


class TransformCurrency(transform_csv.TransformCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True)
    table = luigi.EnumParameter(enum=CurrencyTable)

    def output(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.csv".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        target_dir = "_".join(["transform", self.table.value])
        target_path = path.join(
            self.output_dir,
            target_dir,
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        return extract_batch.ExtractBatchTask(
            extract_datetime=self.extract_datetime,
            json_patch_path="./patch/currency.json",
            json_schema_path="./schema/gw2/v2/currencies/index.json",
            output_dir=self.output_dir,
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/currencies",
        )

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
                        "original": currency["description"],
                    }
                ]
            case CurrencyTable.CurrencyName:
                return [
                    {
                        "app_name": "gw2",
                        "currency_id": currency["id"],
                        "lang_tag": self.lang_tag.value,
                        "original": currency["name"],
                    }
                ]
            case _:
                raise RuntimeError("Unexpected table name")
