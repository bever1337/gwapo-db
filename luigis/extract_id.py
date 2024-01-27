import datetime
import jsonschema
import json
import luigi
import os
import requests


class ExtractId(luigi.Task):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    output_dir = luigi.PathParameter()
    schema = luigi.PathParameter(exists=True)
    url = luigi.Parameter()

    def output(self):
        target_filename = os.path.extsep.join(
            [self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"), "json"]
        )
        output_path = os.path.join(self.output_dir, target_filename)
        return luigi.LocalTarget(path=output_path)

    def run(self):
        response = requests.get(url=self.url)
        if response.status_code != 200:
            raise RuntimeError("Expected status code 200")
        response_json = response.json()

        with open(file=self.schema, mode="r") as fp:
            validator = jsonschema.Draft202012Validator(schema=json.load(fp))
        validator.validate(response_json)

        with self.output().open("w") as write_target:
            write_target.writelines(
                ["".join([str(index), "\n"]) for index in response_json]
            )
