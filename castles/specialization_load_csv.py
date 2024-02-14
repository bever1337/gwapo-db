import datetime
import luigi
from psycopg import sql

import common
from tasks import load_csv
import lang_load
import profession_load_csv
import specialization_transform_csv


class WrapSpecialization(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvSpecialization(**args)
        yield LoadCsvSpecializationName(**args)


class LoadCsvSpecializationTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "specialization"


class LoadCsvSpecialization(LoadCsvSpecializationTask):
    table = "specialization"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.specialization AS target_specialization
USING tempo_specialization AS source_specialization ON
  target_specialization.profession_id = source_specialization.profession_id
  AND target_specialization.specialization_id = source_specialization.specialization_id
WHEN MATCHED
  AND target_specialization.background != source_specialization.background
  OR target_specialization.elite != source_specialization.elite
  OR target_specialization.icon != source_specialization.icon THEN
  UPDATE SET
    (background, elite, icon) = (source_specialization.background,
      source_specialization.elite, source_specialization.icon)
WHEN NOT MATCHED THEN
  INSERT (background, elite, icon, profession_id, specialization_id)
    VALUES (source_specialization.background, source_specialization.elite,
      source_specialization.icon, source_specialization.profession_id,
      source_specialization.specialization_id);
"""
    )

    def requires(self):
        return {
            self.table: specialization_transform_csv.TransformCsvSpecialization(
                lang_tag=self.lang_tag
            ),
            "profession": profession_load_csv.LoadCsvProfession(lang_tag=self.lang_tag),
        }


class LoadCsvSpecializationName(LoadCsvSpecializationTask):
    table = "specialization_name"

    postcopy_sql = sql.Composed(
        [
            lang_load.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_specialization_name")
            ),
            lang_load.merge_into_placed_copy.format(
                table_name=sql.Identifier("specialization_name"),
                temp_table_name=sql.Identifier("tempo_specialization_name"),
                pk_name=sql.Identifier("specialization_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: specialization_transform_csv.TransformCsvSpecializationName(
                lang_tag=self.lang_tag
            ),
            "lang": lang_load.LangLoad(),
            "profession": profession_load_csv.LoadCsvProfession(lang_tag=self.lang_tag),
            "specialization": LoadCsvSpecialization(lang_tag=self.lang_tag),
        }
