import datetime
import jsonschema
import json
import luigi
import os
import requests

import config
import common


class ExtractIdTask(luigi.Task):
    json_schema_path = luigi.PathParameter(exists=True)
    url = luigi.Parameter()

    def output(self):
        gwapo_config = config.gconfig()
        with open(self.json_schema_path) as json_schema_file:
            json_schema = json.load(fp=json_schema_file)
        schema_id: str = json_schema["$id"]
        schema_id_no_ext, _ = os.path.splitext(schema_id)
        schema_id_as_filename = schema_id_no_ext.replace(os.path.sep, "_")
        output_folder = "_".join(["extract", "id", schema_id_as_filename])

        return common.from_output_params(
            output_dir=os.path.join(gwapo_config.output_dir, output_folder),
            extract_datetime=gwapo_config.extract_datetime,
            params={},
            ext="ndjson",
        )

    def run(self):
        response = requests.get(url=self.url)
        if response.status_code != 200:
            raise RuntimeError("Expected status code 200")
        response_json = response.json()

        with open(file=self.json_schema_path, mode="r") as fp:
            jsonschema.Draft202012Validator(schema=json.load(fp)).validate(
                response_json
            )

        with self.output().open("w") as write_target:
            write_target.writelines(
                ["".join([str(entity_id), "\n"]) for entity_id in response_json]
            )
