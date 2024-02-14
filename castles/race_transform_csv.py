import datetime
import luigi

import common
import race_extract
from tasks import transform_csv


class TransformCsvRaceTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "race"

    def requires(self):
        return race_extract.ExtractBatch(lang_tag=self.lang_tag)


class TransformCsvRace(TransformCsvRaceTask):
    def get_rows(self, race):
        return [{"race_id": race["id"]}]


class TransformCsvRaceName(TransformCsvRaceTask):
    def get_rows(self, race):
        return [
            {
                "app_name": "gw2",
                "lang_tag": self.lang_tag.value,
                "original": common.to_xhmtl_fragment(race["name"]),
                "race_id": race["id"],
            }
        ]
