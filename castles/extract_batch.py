import itertools
import jsonschema
import json
import luigi
import os
import requests
import time

import config
import extract_id


class ExtractBatchTask(luigi.Task):
    json_schema_path = luigi.PathParameter(exists=True)
    url_params = luigi.DictParameter(default={})
    url = luigi.Parameter()

    def output(self):
        gwapo_config = config.gconfig()
        return luigi.LocalTarget(
            path=os.path.join(
                gwapo_config.output_dir,
                self.get_task_family(),
                os.path.extsep.join([self.task_id, "ndjson"]),
            )
        )

    def requires(self):
        return extract_id.ExtractIdTask(
            json_schema_path=self.json_schema_path,
            url=self.url,
        )

    def run(self):
        self.set_status_message("Starting")

        with open(self.json_schema_path) as json_schema_file:
            json_schema = json.load(fp=json_schema_file)
        # because schema is union type, this could validate unexpected data
        validator = jsonschema.Draft202012Validator(
            schema={"items": json_schema, "type": "array"}
        )

        with (
            self.input().open("r") as r_input_file,
            self.output().open("w") as write_target,
        ):
            self.set_status_message("Count: {current:d}".format(current=0))
            for index, id_batch in enumerate(itertools.batched(r_input_file, 200)):
                next_params = dict(self.url_params)
                next_params["ids"] = ",".join(
                    [str(json.loads(id)).strip() for id in id_batch]
                )
                response = requests.get(url=self.url, params=next_params)

                if response.status_code != 200:
                    raise RuntimeError("Expected status code 200")
                response_json: list = response.json()
                validator.validate(response_json)
                write_target.writelines(
                    "".join([json.dumps(entity), "\n"]) for entity in response_json
                )

                if index % 100 == 0:
                    processed_so_far = (index * 200) + len(id_batch)
                    self.set_status_message(
                        "Count: {current:d}".format(current=processed_so_far)
                    )
                time.sleep(1 / 5)
