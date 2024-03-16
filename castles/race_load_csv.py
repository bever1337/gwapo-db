import luigi
from psycopg import sql

import common
import lang_load
import race_transform_csv
from tasks import config
from tasks import load_csv


class WrapRace(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvRace(**args)
        yield LoadCsvRaceName(**args)


class WrapRaceTranslate(luigi.WrapperTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        for lang_tag in common.LangTag:
            if lang_tag == self.original_lang_tag:
                continue
            yield LoadCsvRaceNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                task_datetime=self.task_datetime,
                translation_lang_tag=lang_tag,
            )


class LoadCsvRaceTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "race"


class LoadCsvRace(LoadCsvRaceTask):
    table = "race"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.race AS target_race
USING tempo_race AS source_race ON target_race.race_id = source_race.race_id
WHEN NOT MATCHED THEN
  INSERT (race_id)
    VALUES (source_race.race_id);
"""
    )

    def requires(self):
        return {self.table: race_transform_csv.TransformCsvRace(lang_tag=self.lang_tag)}


class LoadCsvRaceName(lang_load.LangLoadCopySourceTask):
    id_attributes = [("race_id", sql.SQL("text NOT NULL"))]
    table = "race_name"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "race"

    def requires(self):
        return {
            self.table: race_transform_csv.TransformCsvRaceName(lang_tag=self.lang_tag),
            "race": LoadCsvRace(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }


class LoadCsvRaceNameTranslation(lang_load.LangLoadCopyTargetTask):
    id_attributes = [("race_id", sql.SQL("text NOT NULL"))]
    table = "race_name_context"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "race"
    widget_table = "race_name"

    def requires(self):
        return {
            self.table: race_transform_csv.TransformCsvRaceNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                translation_lang_tag=self.translation_lang_tag,
            ),
            "_": LoadCsvRaceName(lang_tag=self.original_lang_tag),
        }
