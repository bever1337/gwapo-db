import jsonschema
import json
import luigi
import os
import requests

from tasks import config


class ExtractIdTask(luigi.Task):
    json_schema_path = luigi.PathParameter(exists=True)
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

    def run(self):
        response = requests.get(url=str(self.url))
        if response.status_code != 200:
            raise RuntimeError("Expected status code 200")
        response_json = response.json()

        with open(file=str(self.json_schema_path), mode="r") as fp:
            jsonschema.Draft202012Validator(schema=json.load(fp)).validate(
                response_json
            )

        with self.output().open("w") as write_target:
            write_target.writelines(
                ["".join([json.dumps(entity_id), "\n"]) for entity_id in response_json]
            )
