import itertools
import jsonschema
import json
import luigi
import os
import requests
import time

from tasks import config


class ExtractBatchTask(luigi.Task):
    json_schema_path = luigi.PathParameter(exists=True)
    url_params = luigi.DictParameter()
    url = luigi.Parameter()

    def output(self):
        gwapo_config = config.gconfig()
        return luigi.LocalTarget(
            path=os.path.join(
                str(gwapo_config.output_dir),
                self.get_task_family(),
                os.path.extsep.join([self.task_id, "ndjson"]),
            )
        )

    def requires(self):
        raise NotImplementedError()

    def run(self):
        self.set_status_message("Starting")
        self.set_progress_percentage(0)

        input_file: luigi.LocalTarget = self.input()
        input_file_size = os.stat(input_file.path).st_size
        approx_bytes_processed = 0
        progress_percentage = 0

        with open(str(self.json_schema_path)) as json_schema_file:
            json_schema = json.load(fp=json_schema_file)
        # because schema is union type, this could validate unexpected data
        validator = jsonschema.Draft202012Validator(
            schema={"items": json_schema, "type": "array"}
        )

        with (
            input_file.open("r") as r_input_file,
            self.output().open("w") as write_target,
        ):
            self.set_status_message("Extracting")
            for id_batch in itertools.batched(r_input_file, 100):
                next_params = dict(self.url_params)
                next_params["ids"] = ",".join(
                    [str(json.loads(id)).strip() for id in id_batch]
                )
                response = requests.get(url=self.url, params=next_params)

                if response.status_code != 200:
                    print("ERROR!")
                    print(next_params)
                    print(response)
                    continue
                response_json: list = response.json()
                validator.validate(response_json)
                write_target.writelines(
                    "".join([json.dumps(entity), "\n"]) for entity in response_json
                )

                approx_bytes_processed = approx_bytes_processed + len(
                    next_params["ids"]
                )
                next_progress_percentage = round(
                    (approx_bytes_processed / input_file_size) * 100
                )
                if next_progress_percentage != progress_percentage:
                    progress_percentage = next_progress_percentage
                    self.set_progress_percentage(progress_percentage)
                time.sleep(1 / 4)
