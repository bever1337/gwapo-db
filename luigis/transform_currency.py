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
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.json".format(
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
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.json".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        return extract_batch.ExtractBatch(
            entity_schema="../schema/gw2/v2/currencies/currency.json",
            extract_datetime=self.extract_datetime,
            extract_dir=path.join(self.output_dir, "extract_currency_id"),
            id_schema="../schema/gw2/v2/currencies/index.json",
            output_file=path.join(
                self.output_dir,
                "extract_currency",
                target_filename,
            ),
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/currencies",
        )

    def run(self):
        with self.input().open("r") as currency_input_file:
            currency_json = json.load(fp=currency_input_file)

        with open("transformations_currency.json", "r") as ro_transform:
            transform_json = json.load(fp=ro_transform)

        transform_dict = {}
        for currency_transform in transform_json:
            transform_dict[currency_transform["id"]] = currency_transform

        final_currency_json = []
        for currency in currency_json:
            currency_id = currency["id"]
            if currency_id == 74:
                continue

            transform = transform_dict[currency_id]
            currency["categories"] = transform["categories"]
            currency["deprecated"] = transform["deprecated"]

            final_currency_json.append(currency)

        with self.output().open("w") as w_output_file:
            w_output_file.write(json.dumps(final_currency_json))
