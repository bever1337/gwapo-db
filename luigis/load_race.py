import datetime
import luigi
from os import path
from psycopg import sql

import common
import load_csv
import load_lang
import transform_race


class SeedRace(luigi.WrapperTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)

    def requires(self):
        args = {
            "extract_datetime": self.extract_datetime,
            "lang_tag": self.lang_tag,
            "output_dir": self.output_dir,
        }
        yield LoadRace(**args)
        yield LoadRaceName(**args)


class LoadRaceTask(load_csv.LoadCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)
    table = luigi.EnumParameter(enum=transform_race.RaceTable)

    def output(self):
        output_folder_name = "_".join(["load", self.table.value])
        return common.from_output_params(
            output_dir=path.join(self.output_dir, output_folder_name),
            extract_datetime=self.extract_datetime,
            params={"lang": self.lang_tag.value},
            ext="txt",
        )


class LoadRace(LoadRaceTask):
    table = transform_race.RaceTable.Race

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.race AS target_race
USING tempo_race AS source_race
    ON target_race.race_id = source_race.race_id
WHEN NOT MATCHED THEN
    INSERT (race_id)
        VALUES (source_race.race_id);
"""
    )

    def requires(self):
        return {
            self.table.value: transform_race.TransformRace(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
                table=self.table,
            )
        }


class LoadRaceName(LoadRaceTask):
    table = transform_race.RaceTable.RaceName

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_race_name")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("race_name"),
                temp_table_name=sql.Identifier("tempo_race_name"),
                pk_name=sql.Identifier("race_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table.value: transform_race.TransformRace(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
                table=self.table,
            ),
            transform_race.RaceTable.Race.value: LoadRace(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
            ),
        }
