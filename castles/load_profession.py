import datetime
import luigi
from os import path
from psycopg import sql

import common
import config
import load_csv
import load_lang
import transform_profession


class WrapProfession(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        args = {"lang_tag": self.lang_tag}
        yield LoadProfession(**args)
        yield LoadProfessionName(**args)


class LoadProfessionTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    table = luigi.EnumParameter(enum=transform_profession.ProfessionTable)

    def output(self):
        gwapo_config = config.gconfig()
        output_folder_name = "_".join(["load", self.table.value])
        return common.from_output_params(
            output_dir=path.join(gwapo_config.output_dir, output_folder_name),
            extract_datetime=gwapo_config.extract_datetime,
            params={"lang": self.lang_tag.value, "v": "2019-12-19T00:00:00.000Z"},
            ext="txt",
        )


class LoadProfession(LoadProfessionTask):
    table = transform_profession.ProfessionTable.Profession

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
            self.table.value: transform_profession.TransformProfession(
                lang_tag=self.lang_tag, table=self.table
            )
        }


class LoadProfessionName(LoadProfessionTask):
    table = transform_profession.ProfessionTable.ProfessionName

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_profession_name")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("profession_name"),
                temp_table_name=sql.Identifier("tempo_profession_name"),
                pk_name=sql.Identifier("profession_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table.value: transform_profession.TransformProfession(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_profession.ProfessionTable.Profession.value: LoadProfession(
                lang_tag=self.lang_tag
            ),
            "lang": load_lang.LoadLang(),
        }
