import luigi
from psycopg import sql

import common
import load_csv
import load_lang
import load_profession
import transform_specialization


class WrapSpecialization(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        args = {"lang_tag": self.lang_tag}
        yield LoadSpecialization(**args)
        yield LoadSpecializationName(**args)


class LoadSpecializationTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)


class LoadSpecialization(LoadSpecializationTask):
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
            self.table: transform_specialization.TransformSpecialization(
                lang_tag=self.lang_tag
            ),
            "profession": load_profession.LoadProfession(lang_tag=self.lang_tag),
        }


class LoadSpecializationName(LoadSpecializationTask):
    table = "specialization_name"

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_specialization_name")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("specialization_name"),
                temp_table_name=sql.Identifier("tempo_specialization_name"),
                pk_name=sql.Identifier("specialization_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: transform_specialization.TransformSpecializationName(
                lang_tag=self.lang_tag
            ),
            "lang": load_lang.LoadLang(),
            "profession": load_profession.LoadProfession(lang_tag=self.lang_tag),
            "specialization": LoadSpecialization(lang_tag=self.lang_tag),
        }
