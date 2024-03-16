import luigi
from psycopg import sql

import common
import lang_load
import profession_load_csv
import specialization_transform_csv
from tasks import config
from tasks import load_csv


class WrapSpecialization(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvSpecialization(**args)
        yield LoadCsvSpecializationName(**args)


class WrapSpecializationTranslate(luigi.WrapperTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        for lang_tag in common.LangTag:
            if lang_tag == self.original_lang_tag:
                continue
            yield LoadCsvSpecializationNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                task_datetime=self.task_datetime,
                translation_lang_tag=lang_tag,
            )


class LoadCsvSpecializationTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
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


class LoadCsvSpecializationName(lang_load.LangLoadCopySourceTask):
    id_attributes = [("specialization_id", sql.SQL("integer NOT NULL"))]
    table = "specialization_name"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "specialization"

    def requires(self):
        return {
            self.table: specialization_transform_csv.TransformCsvSpecializationName(
                lang_tag=self.lang_tag
            ),
            "lang": lang_load.LangLoad(),
            "profession": profession_load_csv.LoadCsvProfession(lang_tag=self.lang_tag),
            "specialization": LoadCsvSpecialization(lang_tag=self.lang_tag),
        }


class LoadCsvSpecializationNameTranslation(lang_load.LangLoadCopyTargetTask):
    id_attributes = [("specialization_id", sql.SQL("integer NOT NULL"))]
    table = "specialization_name_context"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "specialization"
    widget_table = "specialization_name"

    def requires(self):
        return {
            self.table: specialization_transform_csv.TransformCsvSpecializationNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                translation_lang_tag=self.translation_lang_tag,
            ),
            "_": LoadCsvSpecializationName(lang_tag=self.original_lang_tag),
        }
