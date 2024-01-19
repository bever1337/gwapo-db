import datetime
import jsonschema
import luigi
from os import path
import requests


class ExtractRace(luigi.Task):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)

    def output(self):
        target_filename = "{timestamp:s}.json".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
        )
        target_path = path.join(
            self.output_dir,
            "extract_race",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def run(self):
        races_response = requests.get("https://api.guildwars2.com/v2/races")
        if races_response.status_code != 200:
            raise RuntimeError("Expected status code 200")
        races_json = races_response.json()
        jsonschema.validate(instance=races_json, schema=v2_races_schema)

        with self.output().open("w") as write_target:
            write_target.write(races_response.text)


v2_races_schema = {"items": {"type": "string"}, "type": "array"}