import csv
import datetime
import json
import luigi
from os import path

import common
import extract_batch


class TransformCurrency(luigi.Task):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True)

    def output(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.csv".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        target_path = path.join(
            self.output_dir,
            "transform_currency",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        return extract_batch.ExtractBatch(
            entity_schema="../schema/gw2/v2/currencies/currency.json",
            extract_datetime=self.extract_datetime,
            output_dir=self.output_dir,
            id_schema="../schema/gw2/v2/currencies/index.json",
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/currencies",
        )

    def run(self):
        with open("transformations_currency.json", "r") as ro_transform:
            transform_json = json.load(fp=ro_transform)

        transform_dict = {}
        for currency_transform in transform_json:
            transform_dict[currency_transform["id"]] = currency_transform

        with (
            self.input().open("r") as r_input_file,
            self.output().open("w") as w_output_file,
        ):
            csv_writer = csv.DictWriter(
                w_output_file,
                fieldnames=["currency_id", "deprecated", "icon", "presentation_order"],
            )
            csv_writer.writeheader()

            for currency_line in r_input_file:
                currency = json.loads(currency_line)
                currency_id = currency["id"]
                if currency_id == 74:
                    continue
                transform = transform_dict[currency_id]
                csv_writer.writerow(
                    {
                        "currency_id": currency_id,
                        "deprecated": transform["deprecated"],
                        "icon": currency["icon"],
                        "presentation_order": currency["order"],
                    }
                )
