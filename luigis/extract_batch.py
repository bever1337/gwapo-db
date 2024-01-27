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
        self.set_progress_percentage(0)
        self.set_status_message("Progress: 0 / Unknown")

        input_target: luigi.LocalTarget = self.input()
        with input_target.open("r") as input_file:
            id_json: list = json.load(input_file)

        with open(self.entity_schema) as entity_schema_file:
            schema = json.load(fp=entity_schema_file)
        validator = jsonschema.Draft202012Validator(
            schema={"items": schema, "type": "array"}
        )

        id_len = len(id_json)
        progress = 0
        self.set_progress_percentage(progress)
        self.set_status_message(
            "Progress: {current:d} / {total:d}".format(current=progress, total=id_len)
        )
        with self.output().open("w") as write_target:
            for index, id_batch in enumerate(itertools.batched(id_json, 200)):
                next_params = dict(self.url_params)
                next_params["ids"] = ",".join([str(id) for id in id_batch])
                response = requests.get(url=self.url, params=next_params)

                if response.status_code != 200:
                    raise RuntimeError("Expected status code 200")
                response_json = response.json()
                validator.validate(response_json)

                write_target.writelines(
                    ["".join([json.dumps(entity), "\n"]) for entity in response_json]
                )

                processed_so_far = (index * 200) + len(id_batch)
                next_progress = round((processed_so_far / id_len) * 100)
                if next_progress != progress:
                    progress = next_progress
                    self.set_progress_percentage(progress)
                    self.set_status_message(
                        "Progress: {current:d} / {total:d}".format(
                            current=processed_so_far, total=id_len
                        )
                    )
                time.sleep(1 / 4)
