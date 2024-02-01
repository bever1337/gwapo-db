import datetime
import luigi
from os import path
from psycopg import sql

import common
import load_csv
import load_lang
import transform_profession


class LoadProfessionTask(load_csv.LoadCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)
    table = luigi.EnumParameter(enum=transform_profession.ProfessionTable)

    def output(self):
        output_folder_name = "_".join(["load", self.table.value])
        return common.from_output_params(
            output_dir=path.join(self.output_dir, output_folder_name),
            extract_datetime=self.extract_datetime,
            params={"lang": self.lang_tag.value, "v": "2019-12-19T00:00:00.000Z"},
            ext="txt",
        )

    def requires(self):
        return transform_profession.TransformProfession(
            extract_datetime=self.extract_datetime,
            lang_tag=self.lang_tag,
            output_dir=self.output_dir,
            table=self.table,
        )


class LoadProfession(LoadProfessionTask):
    table = transform_profession.ProfessionTable.Profession

    precopy_sql = load_csv.create_temporary_table.format(
        temp_table_name=sql.Identifier("tempo_profession"),
        table_name=sql.Identifier("profession"),
    )

    copy_sql = load_csv.copy_from_stdin.format(
        temp_table_name=sql.Identifier("tempo_profession")
    )

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.profession AS target_profession
USING tempo_profession AS source_profession
ON
  target_profession.profession_id = source_profession.profession_id
WHEN MATCHED
  AND target_profession.code != source_profession.code 
  OR target_profession.icon_big != source_profession.icon_big
  OR target_profession.icon != source_profession.icon THEN
  UPDATE SET
    (code, icon_big, icon) = (source_profession.code,
      source_profession.icon_big,
      source_profession.icon)
WHEN NOT MATCHED THEN
  INSERT (code, icon_big, icon, profession_id)
    VALUES (source_profession.code,
      source_profession.icon_big,
      source_profession.icon,
      source_profession.profession_id);
"""
    )


class LoadProfessionName(LoadProfessionTask):
    table = transform_profession.ProfessionTable.ProfessionName

    precopy_sql = load_csv.create_temporary_table.format(
        temp_table_name=sql.Identifier("tempo_profession_name"),
        table_name=sql.Identifier("profession_name"),
    )

    copy_sql = load_csv.copy_from_stdin.format(
        temp_table_name=sql.Identifier("tempo_profession_name")
    )

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
