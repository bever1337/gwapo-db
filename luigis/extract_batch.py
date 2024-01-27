import datetime
import itertools
import jsonschema
import json
import luigi
import os
import requests
import time

import extract_id


class ExtractBatch(luigi.Task):
    entity_schema = luigi.PathParameter(exists=True)
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    id_schema = luigi.PathParameter(exists=True)
    output_dir = luigi.PathParameter(absolute=True, exists=True)
    url_params = luigi.DictParameter(default={})
    url = luigi.Parameter()

    def output(self):
        # foo/bar/baz/{resource}/{filename}.{extension}
        norm_entity_schema_path = os.path.normpath(self.entity_schema)
        resource = norm_entity_schema_path.split(os.sep)[-2:][0]
        output_folder = "_".join(["extract", resource])
        formatted_datetime = self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z")
        filename_params = "__".join(
            ["_".join([key, str(value)]) for key, value in self.url_params.items()]
        )
        datetimed_filename_params = "__".join([formatted_datetime, filename_params])
        output_filename = os.path.extsep.join([datetimed_filename_params, "ndjson"])
        output_path = os.path.join(self.output_dir, output_folder, output_filename)
        return luigi.LocalTarget(path=output_path)

    def requires(self):
        # foo/bar/baz/{resource}/{filename}.{extension}
        norm_id_schema_path = os.path.normpath(self.id_schema)
        resource = norm_id_schema_path.split(os.sep)[-2:][0]
        output_folder = "_".join(["extract", resource, "index"])
        require_dir = os.path.join(self.output_dir, output_folder)
        return extract_id.ExtractId(
            extract_datetime=self.extract_datetime,
            output_dir=require_dir,
            schema=self.id_schema,
            url=self.url,
        )

    def run(self):
        self.set_status_message("Starting")

        with open(self.entity_schema) as entity_schema_file:
            validator = jsonschema.Draft202012Validator(
                schema={"items": json.load(fp=entity_schema_file), "type": "array"}
            )

        progress = 0
        self.set_progress_percentage(progress)
        self.set_status_message(
            "Progress: {current:d} / {total:d}".format(current=progress, total=0)
        )
        with (
            self.input().open("r") as r_input_file,
            self.output().open("w") as write_target,
        ):
            self.set_status_message("Count: {current:d}".format(current=0))
            for index, id_batch in enumerate(itertools.batched(r_input_file, 200)):
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

                if index % 100 == 0:
                    processed_so_far = (index * 200) + len(id_batch)
                    self.set_status_message(
                        "Count: {current:d}".format(current=processed_so_far)
                    )

                time.sleep(1 / 4)
