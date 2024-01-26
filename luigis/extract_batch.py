import datetime
import itertools
import jsonschema
import json
import luigi
import requests
import time

import extract_id


class ExtractBatch(luigi.Task):
    entity_schema = luigi.PathParameter(exists=True)
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    extract_dir = luigi.PathParameter()
    id_schema = luigi.PathParameter(exists=True)
    output_file = luigi.PathParameter(absolute=True)
    url_params = luigi.DictParameter(default={})
    url = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(path=self.output_file)

    def requires(self):
        return extract_id.ExtractId(
            extract_datetime=self.extract_datetime,
            output_dir=self.extract_dir,
            schema=self.id_schema,
            url=self.url,
        )

    def run(self):
        input_target: luigi.LocalTarget = self.input()
        with input_target.open("r") as input_file:
            id_json: list = json.load(input_file)

        with open(self.entity_schema) as entity_schema_file:
            schema = json.load(fp=entity_schema_file)
        validator = jsonschema.Draft202012Validator(
            schema={"items": schema, "type": "array"}
        )

        entities = []

        for id_batch in itertools.batched(id_json, 200):
            next_params = dict(self.url_params)
            next_params["ids"] = ",".join(str(id) for id in id_batch)
            response = requests.get(url=self.url, params=next_params)
            if response.status_code != 200:
                raise RuntimeError("Expected status code 200")
            response_json = response.json()
            validator.validate(response_json)
            entities.extend(response_json)
            time.sleep(1 / 6)

        with self.output().open("w") as write_target:
            json.dump(obj=entities, fp=write_target)
