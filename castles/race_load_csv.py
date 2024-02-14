import datetime
import luigi
from psycopg import sql

import common
from tasks import load_csv
import lang_load
import race_transform_csv


class WrapRace(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvRace(**args)
        yield LoadCsvRaceName(**args)


class LoadCsvRaceTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
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


class LoadCsvRaceName(LoadCsvRaceTask):
    table = "race_name"

    postcopy_sql = sql.Composed(
        [
            lang_load.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_race_name")
            ),
            lang_load.merge_into_placed_copy.format(
                table_name=sql.Identifier("race_name"),
                temp_table_name=sql.Identifier("tempo_race_name"),
                pk_name=sql.Identifier("race_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: race_transform_csv.TransformCsvRaceName(lang_tag=self.lang_tag),
            "race": LoadCsvRace(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }
