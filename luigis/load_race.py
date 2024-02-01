import datetime
import luigi
from os import path
from psycopg import sql

import common
import load_csv
import load_lang
import transform_race


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

    def requires(self):
        return transform_race.TransformRace(
            extract_datetime=self.extract_datetime,
            lang_tag=self.lang_tag,
            output_dir=self.output_dir,
            table=self.table,
        )


class LoadRace(LoadRaceTask):
    table = transform_race.RaceTable.Race

    precopy_sql = load_csv.create_temporary_table.format(
        temp_table_name=sql.Identifier("tempo_race"),
        table_name=sql.Identifier("race"),
    )

    copy_sql = load_csv.copy_from_stdin.format(
        temp_table_name=sql.Identifier("tempo_race")
    )

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


class LoadRaceName(LoadRaceTask):
    table = transform_race.RaceTable.RaceName

    precopy_sql = load_csv.create_temporary_table.format(
        temp_table_name=sql.Identifier("tempo_race_name"),
        table_name=sql.Identifier("race_name"),
    )

    copy_sql = load_csv.copy_from_stdin.format(
        temp_table_name=sql.Identifier("tempo_race_name")
    )

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
