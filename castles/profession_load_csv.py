import datetime
import luigi
from psycopg import sql

import common
from tasks import load_csv
import lang_load
import profession_transform_csv


class WrapProfession(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvProfession(**args)
        yield LoadCsvProfessionName(**args)


class LoadCsvProfessionTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "profession"


class LoadCsvProfession(LoadCsvProfessionTask):
    table = "profession"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.profession AS target_profession
USING tempo_profession AS source_profession ON target_profession.profession_id
  = source_profession.profession_id
WHEN MATCHED
  AND target_profession.code != source_profession.code
  OR target_profession.icon_big != source_profession.icon_big
  OR target_profession.icon != source_profession.icon THEN
  UPDATE SET
    (code, icon_big, icon) = (source_profession.code,
      source_profession.icon_big, source_profession.icon)
WHEN NOT MATCHED THEN
  INSERT (code, icon_big, icon, profession_id)
    VALUES (source_profession.code, source_profession.icon_big,
      source_profession.icon, source_profession.profession_id);
"""
    )

    def requires(self):
        return {
            self.table: profession_transform_csv.TransformCsvProfession(
                lang_tag=self.lang_tag
            )
        }


class LoadCsvProfessionName(LoadCsvProfessionTask):
    table = "profession_name"

    postcopy_sql = sql.Composed(
        [
            lang_load.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_profession_name")
            ),
            lang_load.merge_into_placed_copy.format(
                table_name=sql.Identifier("profession_name"),
                temp_table_name=sql.Identifier("tempo_profession_name"),
                pk_name=sql.Identifier("profession_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: profession_transform_csv.TransformCsvProfessionName(
                lang_tag=self.lang_tag
            ),
            "profession": LoadCsvProfession(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }
