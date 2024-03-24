import luigi

import common
import race_extract
from tasks import config
from tasks import transform_csv


class TransformCsvRaceTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
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


class TransformCsvRaceNameTranslation(transform_csv.TransformCsvTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "race"
    translation_lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def get_rows(self, race):
        return [
            {
                "app_name": self.app_name,
                "original_lang_tag": self.original_lang_tag.value,
                "race_id": race["id"],
                "translation_lang_tag": self.translation_lang_tag.value,
                "translation": common.to_xhmtl_fragment(race["name"]),
            }
        ]

    def requires(self):
        return race_extract.ExtractBatch(lang_tag=self.translation_lang_tag)
