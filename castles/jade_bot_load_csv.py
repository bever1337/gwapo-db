import luigi
from psycopg import sql

import common
import item_load_csv
import jade_bot_transform_csv
import lang_load
from tasks import config
from tasks import load_csv


class WrapJadeBot(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvJadeBot(**args)
        yield LoadCsvJadeBotDescription(**args)
        yield LoadCsvJadeBotName(**args)


class WrapJadeBotTranslate(luigi.WrapperTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        for lang_tag in common.LangTag:
            if lang_tag == self.original_lang_tag:
                continue
            yield LoadCsvJadeBotDescriptionTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                task_datetime=self.task_datetime,
                translation_lang_tag=lang_tag,
            )
            yield LoadCsvJadeBotNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                task_datetime=self.task_datetime,
                translation_lang_tag=lang_tag,
            )


class LoadCsvJadeBotTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "jade_bot"


class LoadCsvJadeBot(LoadCsvJadeBotTask):
    table = "jade_bot"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.jade_bot AS target_jade_bot
USING tempo_jade_bot AS source_jade_bot ON target_jade_bot.jade_bot_id =
  source_jade_bot.jade_bot_id
WHEN NOT MATCHED THEN
  INSERT (jade_bot_id)
    VALUES (source_jade_bot.jade_bot_id);
"""
    )

    def requires(self):
        return {
            self.table: jade_bot_transform_csv.TransformCsvJadeBot(
                lang_tag=self.lang_tag
            )
        }


class LoadCsvJadeBotDescription(lang_load.LangLoadCopySourceTask):
    id_attributes = [("jade_bot_id", sql.SQL("integer NOT NULL"))]
    table = "jade_bot_description"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "jade_bot"

    def requires(self):
        return {
            self.table: jade_bot_transform_csv.TransformCsvJadeBotDescription(
                lang_tag=self.lang_tag
            ),
            "jade_bot": LoadCsvJadeBot(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }


class LoadCsvJadeBotDescriptionTranslation(lang_load.LangLoadCopyTargetTask):
    id_attributes = [("jade_bot_id", sql.SQL("integer NOT NULL"))]
    table = "jade_bot_description_context"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "jade_bot"
    widget_table = "jade_bot_description"

    def requires(self):
        return {
            self.table: jade_bot_transform_csv.TransformCsvJadeBotDescriptionTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                translation_lang_tag=self.translation_lang_tag,
            ),
            "_": LoadCsvJadeBotDescription(lang_tag=self.original_lang_tag),
        }


class LoadCsvJadeBotItem(LoadCsvJadeBotTask):
    table = "jade_bot_item"

    postcopy_sql = item_load_csv.merge_into_item_reference.format(
        cross_table_name=sql.Identifier("jade_bot_item"),
        table_name=sql.Identifier("jade_bot"),
        temp_table_name=sql.Identifier("tempo_jade_bot_item"),
        pk_name=sql.Identifier("jade_bot_id"),
    )

    def requires(self):
        return {
            self.table: jade_bot_transform_csv.TransformCsvJadeBotItem(
                lang_tag=self.lang_tag
            ),
            "jade_bot": LoadCsvJadeBot(lang_tag=self.lang_tag),
            "item": item_load_csv.LoadCsvItem(lang_tag=self.lang_tag),
        }


class LoadCsvJadeBotName(lang_load.LangLoadCopySourceTask):
    id_attributes = [("jade_bot_id", sql.SQL("integer NOT NULL"))]
    table = "jade_bot_name"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "jade_bot"

    def requires(self):
        return {
            self.table: jade_bot_transform_csv.TransformCsvJadeBotName(
                lang_tag=self.lang_tag
            ),
            "jade_bot": LoadCsvJadeBot(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }


class LoadCsvJadeBotNameTranslation(lang_load.LangLoadCopyTargetTask):
    id_attributes = [("jade_bot_id", sql.SQL("integer NOT NULL"))]
    table = "jade_bot_name_context"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "jade_bot"
    widget_table = "jade_bot_name"

    def requires(self):
        return {
            self.table: jade_bot_transform_csv.TransformCsvJadeBotNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                translation_lang_tag=self.translation_lang_tag,
            ),
            "_": LoadCsvJadeBotName(lang_tag=self.original_lang_tag),
        }
