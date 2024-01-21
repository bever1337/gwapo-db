import datetime
import jsonschema
import json
import luigi
from os import path
import requests


class ExtractId(luigi.Task):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    output_dir = luigi.PathParameter()
    schema = luigi.PathParameter(exists=True)
    url = luigi.Parameter()

    def output(self):
        target_filename = "{timestamp:s}.json".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
        )
        target_path = path.join(self.output_dir, target_filename)
        return luigi.LocalTarget(path=target_path)

    def run(self):
        response = requests.get(url=self.url)
        if response.status_code != 200:
            raise RuntimeError("Expected status code 200")
        response_json = response.json()

        with open(file=self.schema, mode="r") as fp:
            schema = json.load(fp=fp)
        jsonschema.validate(instance=response_json, schema=schema)

        with self.output().open("w") as write_target:
            write_target.write(response.text)
