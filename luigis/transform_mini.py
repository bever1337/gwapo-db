import datetime
import json
import luigi
from os import path

import common
import extract_batch


class TransformMini(luigi.Task):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True)

    def output(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.ndjson".format(
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
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.ndjson".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        return extract_batch.ExtractBatch(
            entity_schema="../schema/gw2/v2/minis/mini.json",
            extract_datetime=self.extract_datetime,
            extract_dir=path.join(self.output_dir, "extract_mini_id"),
            id_schema="../schema/gw2/v2/minis/index.json",
            output_file=path.join(
                self.output_dir,
                "extract_mini",
                target_filename,
            ),
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/minis",
        )

    def run(self):
        with open("transformations_mini.json", "r") as ro_transform:
            transform_json = json.load(fp=ro_transform)

        transform_dict = {}
        for mini_transform in transform_json:
            mini_transform_id = mini_transform["id"]
            transform_dict[mini_transform_id] = mini_transform

        with (
            self.input().open("r") as r_input_file,
            self.output().open("w") as w_output_file,
        ):
            for mini_line in r_input_file:
                mini = json.loads(mini_line)
                mini_id = mini["id"]

                transform = transform_dict.get(mini_id)
                if transform != None:
                    mini["item_id"] = transform["item_id"]
                    mini["name"] = transform["name"]

                w_output_file.write("".join([json.dumps(mini), "\n"]))
