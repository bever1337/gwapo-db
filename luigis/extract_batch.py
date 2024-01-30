import copy
import datetime
import itertools
import jsonpatch
import jsonschema
import json
import luigi
import os
import requests
import time

import extract_id


class ExtractBatchTask(luigi.Task):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    json_patch_path = luigi.OptionalPathParameter(
        default="./patch/noop.json", exists=True
    )
    json_schema_path = luigi.PathParameter(exists=True)
    output_dir = luigi.PathParameter(absolute=True, exists=True)
    url_params = luigi.DictParameter(default={})
    url = luigi.Parameter()

    def output(self):
        with open(self.json_schema_path) as json_schema_file:
            json_schema = json.load(fp=json_schema_file)
        schema_id: str = json_schema["$id"]
        schema_id_no_ext, _ = os.path.splitext(schema_id)
        schema_id_as_filename = schema_id_no_ext.replace(os.path.sep, "_")
        output_folder = "_".join(["extract", "batch", schema_id_as_filename])

        formatted_datetime = self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z")
        filename_params = "__".join(
            ["_".join([key, str(value)]) for key, value in self.url_params.items()]
        )
        datetimed_filename_params = "__".join([formatted_datetime, filename_params])
        output_filename = os.path.extsep.join([datetimed_filename_params, "ndjson"])

        output_path = os.path.join(self.output_dir, output_folder, output_filename)
        return luigi.LocalTarget(path=output_path)

    def requires(self):
        return extract_id.ExtractIdTask(
            extract_datetime=self.extract_datetime,
            json_schema_path=self.json_schema_path,
            output_dir=self.output_dir,
            url=self.url,
        )

    def run(self):
        self.set_status_message("Starting")

        with open(self.json_schema_path) as json_schema_file:
            json_schema = json.load(fp=json_schema_file)
        validator = jsonschema.Draft202012Validator(
            schema={"items": json_schema, "type": "array"}
        )

        with open(self.json_patch_path) as json_patch_file:
            json_patches = [
                jsonpatch.JsonPatch(patch) for patch in json.load(fp=json_patch_file)
            ]

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
                next_params["ids"] = ",".join([str(id).strip() for id in id_batch])
                response = requests.get(url=self.url, params=next_params)

                if response.status_code != 200:
                    raise RuntimeError("Expected status code 200")
                response_json: list = response.json()
                validator.validate(response_json)

                for entity in response_json:
                    patched_entity = copy.deepcopy(entity)
                    for patch in json_patches:
                        try:
                            # in_place patches do not allow setting root to None
                            # gwapo patches use an `add` operation to filter out patches
                            # so, accumulate the patched entity and check Noneness afterwards
                            patched_entity = patch.apply(patched_entity, in_place=False)
                        except jsonpatch.JsonPatchTestFailed:
                            # each patch begins with a so-called identity test op
                            # it is expected to fail, try the next patch
                            pass
                    if patched_entity != None:
                        write_target.write("".join([json.dumps(patched_entity), "\n"]))

                if index % 100 == 0:
                    processed_so_far = (index * 200) + len(id_batch)
                    self.set_status_message(
                        "Count: {current:d}".format(current=processed_so_far)
                    )
                time.sleep(1 / 5)
