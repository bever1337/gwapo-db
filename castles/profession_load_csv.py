import luigi
from psycopg import sql

import common
import lang_load
import profession_transform_csv
from tasks import config
from tasks import load_csv


class WrapProfession(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvProfession(**args)
        yield LoadCsvProfessionName(**args)


class WrapProfessionTranslate(luigi.WrapperTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        for lang_tag in common.LangTag:
            if lang_tag == self.original_lang_tag:
                continue
            yield LoadCsvProfessionNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                task_datetime=self.task_datetime,
                translation_lang_tag=lang_tag,
            )


class LoadCsvProfessionTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "profession"


class LoadCsvProfession(LoadCsvProfessionTask):
    table = "profession"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.profession AS target_profession
USING tempo_profession AS source_profession
  ON target_profession.profession_id = source_profession.profession_id
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


class LoadCsvProfessionName(lang_load.LangLoadCopySourceTask):
    id_attributes = [("profession_id", sql.SQL("text NOT NULL"))]
    table = "profession_name"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "profession"

    def requires(self):
        return {
            self.table: profession_transform_csv.TransformCsvProfessionName(
                lang_tag=self.lang_tag
            ),
            "profession": LoadCsvProfession(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }


class LoadCsvProfessionNameTranslation(lang_load.LangLoadCopyTargetTask):
    id_attributes = [("profession_id", sql.SQL("text NOT NULL"))]
    table = "profession_name_context"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "profession"
    widget_table = "profession_name"

    def requires(self):
        return {
            self.table: profession_transform_csv.TransformCsvProfessionNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                translation_lang_tag=self.translation_lang_tag,
            ),
            "_": LoadCsvProfessionName(lang_tag=self.original_lang_tag),
        }
