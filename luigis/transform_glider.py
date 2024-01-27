import datetime
import jsonschema
import json
import luigi
from os import path

import common
import extract_batch


class TransformGlider(luigi.Task):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)

    def output(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.ndjson".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        target_path = path.join(
            self.output_dir,
            "transform_glider",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.ndjson".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        return extract_batch.ExtractBatch(
            entity_schema="../schema/gw2/v2/gliders/glider.json",
            extract_datetime=self.extract_datetime,
            extract_dir=path.join(self.output_dir, "extract_glider_id"),
            id_schema="../schema/gw2/v2/gliders/index.json",
            output_file=path.join(
                self.output_dir,
                "extract_glider",
                target_filename,
            ),
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/gliders",
        )

    def run(self):
        validator = jsonschema.Draft202012Validator(schema=stricter_glider_schema)

        with (
            self.input().open("r") as r_input_file,
            self.output().open("w") as w_output_file,
        ):
            for glider_line in r_input_file:
                glider = json.loads(glider_line)
                glider["unlock_items"] = glider.get("unlock_items", [])
                validator.validate(glider)
                w_output_file.write("".join([json.dumps(glider), "\n"]))


stricter_glider_schema = {
    "$id": "schema/gw2/v2/gliders/glider.json",
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "properties": {
        "default_dyes": {"items": {"type": "integer"}, "type": "array"},
        "description": {"type": "string"},
        "icon": {"format": "uri", "minLength": 1, "type": "string"},
        "id": {"type": "integer"},
        "order": {"type": "integer"},
        "name": {"minLength": 1, "type": "string"},
        "unlock_items": {"items": {"type": "integer"}, "type": "array"},
    },
    "required": [
        "default_dyes",
        "description",
        "icon",
        "id",
        "order",
        "name",
        "unlock_items",
    ],
    "type": "object",
}
