import datetime
import jsonschema
import json
import luigi
import os
import requests


class ExtractIdTask(luigi.Task):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    json_schema_path = luigi.PathParameter(exists=True)
    output_dir = luigi.PathParameter()
    url = luigi.Parameter()

    def output(self):
        with open(self.json_schema_path) as json_schema_file:
            json_schema = json.load(fp=json_schema_file)
        schema_id: str = json_schema["$id"]
        schema_id_no_ext, _ = os.path.splitext(schema_id)
        schema_id_as_filename = schema_id_no_ext.replace(os.path.sep, "_")
        output_folder = "_".join(["extract", "id", schema_id_as_filename])

        formatted_datetime = self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z")
        output_filename = os.path.extsep.join([formatted_datetime, "ndjson"])
        output_path = os.path.join(self.output_dir, output_folder, output_filename)
        return luigi.LocalTarget(path=output_path)

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
