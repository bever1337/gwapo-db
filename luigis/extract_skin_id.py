import datetime
import jsonschema
import luigi
from os import path
import requests


class ExtractSkinId(luigi.Task):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)

    def output(self):
        target_filename = "{timestamp:s}.json".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
        )
        target_path = path.join(
            self.output_dir,
            "extract_skin_id",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def run(self):
        skins_response = requests.get(url="https://api.guildwars2.com/v2/skins")
        if skins_response.status_code != 200:
            raise RuntimeError("Expected status code 200")
        skins_json = skins_response.json()
        jsonschema.validate(instance=skins_json, schema=v2_skins_schema)

        with self.output().open("w") as write_target:
            write_target.write(skins_response.text)


v2_skins_schema = {"items": {"type": "integer"}, "type": "array"}
