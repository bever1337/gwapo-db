import datetime
import jsonschema
import luigi
from os import path
import requests

import common


class ExtractCurrency(luigi.Task):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)

    def output(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.json".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        target_path = path.join(
            self.output_dir,
            "extract_currency",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def run(self):
        currencies_response = requests.get(
            url="https://api.guildwars2.com/v2/currencies",
            params={"ids": "all", "lang": self.lang_tag.value},
        )
        if currencies_response.status_code != 200:
            raise RuntimeError("Expected status code 200")
        currencies_json = currencies_response.json()
        jsonschema.validate(
            instance=currencies_json,
            schema=v2_currencies_schema,
        )

        with self.output().open("w") as write_target:
            write_target.write(currencies_response.text)


v2_currencies_schema = {
    "items": {
        "properties": {
            "description": {"type": "string"},
            "icon": {"type": "string", "format": "uri"},
            "id": {"type": "integer"},
            "order": {"type": "integer"},
            "name": {"type": "string"},
        },
        "required": ["description", "icon", "id", "order", "name"],
        "type": "object",
    },
    "type": "array",
}
