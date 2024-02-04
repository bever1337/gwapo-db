import datetime
import luigi
from os import path
from psycopg import sql


import common
import load_csv
import load_lang
import transform_finisher


class SeedFinisher(luigi.WrapperTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)

    def requires(self):
        args = {
            "extract_datetime": self.extract_datetime,
            "lang_tag": self.lang_tag,
            "output_dir": self.output_dir,
        }
        yield LoadFinisher(**args)
        yield LoadFinisherDetail(**args)
        yield LoadFinisherName(**args)


class LoadFinisherTask(load_csv.LoadCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)
    table = luigi.EnumParameter(enum=transform_finisher.FinisherTable)

    def output(self):
        output_folder_name = "_".join(["load", self.table.value])
        return common.from_output_params(
            output_dir=path.join(self.output_dir, output_folder_name),
            extract_datetime=self.extract_datetime,
            params={"lang": self.lang_tag.value},
            ext="txt",
        )


class LoadFinisher(LoadFinisherTask):
    table = transform_finisher.FinisherTable.Finisher

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.finisher AS target_finisher
USING tempo_finisher AS source_finisher ON target_finisher.finisher_id =
  source_finisher.finisher_id
WHEN MATCHED
  AND target_finisher.icon != source_finisher.icon
  OR target_finisher.presentation_order != source_finisher.presentation_order THEN
  UPDATE SET
    (icon, presentation_order) = (source_finisher.icon, source_finisher.presentation_order)
WHEN NOT MATCHED THEN
  INSERT (finisher_id, icon, presentation_order)
    VALUES (source_finisher.finisher_id, source_finisher.icon,
      source_finisher.presentation_order);
"""
    )

    def requires(self):
        return {
            self.table.value: transform_finisher.TransformFinisher(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
                table=self.table,
            )
        }


class LoadFinisherDetail(LoadFinisherTask):
    table = transform_finisher.FinisherTable.FinisherDetail

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_finisher_detail")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("finisher_detail"),
                temp_table_name=sql.Identifier("tempo_finisher_detail"),
                pk_name=sql.Identifier("finisher_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table.value: transform_finisher.TransformFinisher(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
                table=self.table,
            ),
            transform_finisher.FinisherTable.Finisher.value: LoadFinisher(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
            ),
            "lang": load_lang.LoadLang(
                extract_datetime=self.extract_datetime, output_dir=self.output_dir
            ),
        }


class LoadFinisherName(LoadFinisherTask):
    table = transform_finisher.FinisherTable.FinisherName

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_finisher_name")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("finisher_name"),
                temp_table_name=sql.Identifier("tempo_finisher_name"),
                pk_name=sql.Identifier("finisher_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table.value: transform_finisher.TransformFinisher(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
                table=self.table,
            ),
            transform_finisher.FinisherTable.Finisher.value: LoadFinisher(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
            ),
            "lang": load_lang.LoadLang(
                extract_datetime=self.extract_datetime, output_dir=self.output_dir
            ),
        }
