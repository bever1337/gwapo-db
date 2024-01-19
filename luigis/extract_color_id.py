import datetime
import jsonschema
import luigi
from os import path
import requests


class ExtractColorId(luigi.Task):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)

    def output(self):
        target_filename = "{timestamp:s}.json".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
        )
        target_path = path.join(
            self.output_dir,
            "extract_color_id",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def run(self):
        colors_response = requests.get(url="https://api.guildwars2.com/v2/colors")
        if colors_response.status_code != 200:
            raise RuntimeError("Expected status code 200")
        colors_json = colors_response.json()
        jsonschema.validate(instance=colors_json, schema=v2_colors_schema)

        with self.output().open("w") as write_target:
            write_target.write(colors_response.text)


v2_colors_schema = {"items": {"type": "integer"}, "type": "array"}
