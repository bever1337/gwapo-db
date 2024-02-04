import datetime
import luigi
from os import path
from psycopg import sql

import common
import load_csv
import load_lang
import load_profession
import transform_profession
import transform_specialization


class SeedSpecialization(luigi.WrapperTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)

    def requires(self):
        args = {
            "extract_datetime": self.extract_datetime,
            "lang_tag": self.lang_tag,
            "output_dir": self.output_dir,
        }
        yield LoadSpecialization(**args)
        yield LoadSpecializationName(**args)


class LoadSpecializationTask(load_csv.LoadCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)
    table = luigi.EnumParameter(enum=transform_specialization.SpecializationTable)

    def output(self):
        output_folder_name = "_".join(["load", self.table.value])
        return common.from_output_params(
            output_dir=path.join(self.output_dir, output_folder_name),
            extract_datetime=self.extract_datetime,
            params={"lang": self.lang_tag.value},
            ext="txt",
        )


class LoadSpecialization(LoadSpecializationTask):
    table = transform_specialization.SpecializationTable.Specialization

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
            self.table.value: transform_specialization.TransformSpecialization(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
                table=self.table,
            ),
            transform_profession.ProfessionTable.Profession.value: load_profession.LoadProfession(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
            ),
        }


class LoadSpecializationName(LoadSpecializationTask):
    table = transform_specialization.SpecializationTable.SpecializationName

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
            self.table.value: transform_specialization.TransformSpecialization(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
                table=self.table,
            ),
            "lang": load_lang.LoadLang(
                extract_datetime=self.extract_datetime, output_dir=self.output_dir
            ),
            transform_profession.ProfessionTable.Profession.value: load_profession.LoadProfession(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
            ),
            transform_specialization.SpecializationTable.Specialization.value: LoadSpecialization(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
            ),
        }
