import datetime
import json
import luigi
from os import path

import common
import extract_mini


class TransformMini(luigi.Task):
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
            "transform_mini",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        return extract_mini.ExtractMini(
            extract_datetime=self.extract_datetime, lang_tag=self.lang_tag
        )

    def run(self):
        with self.input().open("r") as mini_input_file:
            mini_json: list[dict] = json.load(fp=mini_input_file)

        with open("transformations_mini.json", "r") as ro_transform:
            transform_json = json.load(fp=ro_transform)

        transform_dict = {}
        for mini_transform in transform_json:
            mini_transform_id = mini_transform["id"]
            transform_dict[mini_transform_id] = mini_transform

        for mini in mini_json:
            mini_id = mini["id"]

            transform = transform_dict.get(mini_id)
            if transform == None:
                continue

            mini["item_id"] = transform["item_id"]
            mini["name"] = transform["name"]

        with self.output().open("w") as w_output_file:
            w_output_file.write(json.dumps(mini_json))
