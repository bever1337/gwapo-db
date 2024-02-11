import luigi
from psycopg import sql

import common
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


class LoadRace(LoadRaceTask):
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
        return {self.table: transform_race.TransformRace(lang_tag=self.lang_tag)}


class LoadRaceName(LoadRaceTask):
    table = "race_name"

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
            self.table: transform_race.TransformRaceName(lang_tag=self.lang_tag),
            "race": LoadRace(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }
