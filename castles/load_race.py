import luigi
from os import path
from psycopg import sql

import common
import config
import load_csv
import load_lang
import transform_race


class WrapRace(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        args = {"lang_tag": self.lang_tag}
        yield LoadRace(**args)
        yield LoadRaceName(**args)


class LoadRaceTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    table = luigi.EnumParameter(enum=transform_race.RaceTable)

    def output(self):
        gwapo_config = config.gconfig()
        output_folder_name = "_".join(["load", self.table.value])
        return common.from_output_params(
            output_dir=path.join(gwapo_config.output_dir, output_folder_name),
            extract_datetime=gwapo_config.extract_datetime,
            params={"lang": self.lang_tag.value},
            ext="txt",
        )


class LoadRace(LoadRaceTask):
    table = transform_race.RaceTable.Race

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
        return {
            self.table.value: transform_race.TransformRace(
                lang_tag=self.lang_tag, table=self.table
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
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_race.RaceTable.Race.value: LoadRace(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }
