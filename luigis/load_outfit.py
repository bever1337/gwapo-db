import datetime
import luigi
from os import path
from psycopg import sql

import common
import load_csv
import load_lang
import transform_outfit


class LoadOutfitTask(load_csv.LoadCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)
    table = luigi.EnumParameter(enum=transform_outfit.OutfitTable)

    def output(self):
        output_folder_name = "_".join(["load", self.table.value])
        return common.from_output_params(
            output_dir=path.join(self.output_dir, output_folder_name),
            extract_datetime=self.extract_datetime,
            params={"lang": self.lang_tag.value},
            ext="txt",
        )

    def requires(self):
        return transform_outfit.TransformOutfit(
            extract_datetime=self.extract_datetime,
            lang_tag=self.lang_tag,
            output_dir=self.output_dir,
            table=self.table,
        )


class LoadOutfit(LoadOutfitTask):
    table = transform_outfit.OutfitTable.Outfit

    precopy_sql = load_csv.create_temporary_table.format(
        temp_table_name=sql.Identifier("tempo_outfit"),
        table_name=sql.Identifier("outfit"),
    )

    copy_sql = load_csv.copy_from_stdin.format(
        temp_table_name=sql.Identifier("tempo_outfit")
    )

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.outfit AS target_outfit
USING tempo_outfit AS source_outfit
ON
  target_outfit.outfit_id = source_outfit.outfit_id
WHEN MATCHED
  AND target_outfit.icon != source_outfit.icon THEN
  UPDATE SET
    icon = source_outfit.icon
WHEN NOT MATCHED THEN
  INSERT (icon, outfit_id)
    VALUES (source_outfit.icon,
      source_outfit.outfit_id);
"""
    )


class LoadOutfitName(LoadOutfitTask):
    table = transform_outfit.OutfitTable.OutfitName

    precopy_sql = load_csv.create_temporary_table.format(
        temp_table_name=sql.Identifier("tempo_outfit_name"),
        table_name=sql.Identifier("outfit_name"),
    )

    copy_sql = load_csv.copy_from_stdin.format(
        temp_table_name=sql.Identifier("tempo_outfit_name")
    )

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_outfit_name")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("outfit_name"),
                temp_table_name=sql.Identifier("tempo_outfit_name"),
                pk_name=sql.Identifier("outfit_id"),
            ),
        ]
    )
