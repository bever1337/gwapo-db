import luigi
from os import path
from psycopg import sql

import common
import config
import load_csv
import load_item
import load_lang
import transform_item
import transform_outfit


class WrapOutfit(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        args = {"lang_tag": self.lang_tag}
        yield LoadOutfit(**args)
        yield LoadOutfitName(**args)


class LoadOutfitTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    table = luigi.EnumParameter(enum=transform_outfit.OutfitTable)

    def output(self):
        gwapo_config = config.gconfig()
        output_folder_name = "_".join(["load", self.table.value])
        return common.from_output_params(
            output_dir=path.join(gwapo_config.output_dir, output_folder_name),
            extract_datetime=gwapo_config.extract_datetime,
            params={"lang": self.lang_tag.value},
            ext="txt",
        )


class LoadOutfit(LoadOutfitTask):
    table = transform_outfit.OutfitTable.Outfit

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.outfit AS target_outfit
USING tempo_outfit AS source_outfit ON target_outfit.outfit_id = source_outfit.outfit_id
WHEN MATCHED
  AND target_outfit.icon != source_outfit.icon THEN
  UPDATE SET
    icon = source_outfit.icon
WHEN NOT MATCHED THEN
  INSERT (icon, outfit_id)
    VALUES (source_outfit.icon, source_outfit.outfit_id);
"""
    )

    def requires(self):
        return {
            self.table.value: transform_outfit.TransformOutfit(
                lang_tag=self.lang_tag, table=self.table
            )
        }


class LoadOutfitItem(LoadOutfitTask):
    table = transform_outfit.OutfitTable.OutfitItem

    postcopy_sql = load_item.merge_into_item_reference.format(
        cross_table_name=sql.Identifier(transform_outfit.OutfitTable.OutfitItem.value),
        table_name=sql.Identifier(transform_outfit.OutfitTable.Outfit.value),
        temp_table_name=sql.Identifier("tempo_outfit_item"),
        pk_name=sql.Identifier("outfit_id"),
    )

    def requires(self):
        return {
            self.table.value: transform_outfit.TransformOutfit(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_outfit.OutfitTable.Outfit.value: LoadOutfit(
                lang_tag=self.lang_tag
            ),
            transform_item.ItemTable.Item.value: load_item.LoadItem(
                lang_tag=self.lang_tag
            ),
        }


class LoadOutfitName(LoadOutfitTask):
    table = transform_outfit.OutfitTable.OutfitName

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

    def requires(self):
        return {
            self.table.value: transform_outfit.TransformOutfit(
                lang_tag=self.lang_tag, table=self.table
            ),
            transform_outfit.OutfitTable.Outfit.value: LoadOutfit(
                lang_tag=self.lang_tag
            ),
            "lang": load_lang.LoadLang(),
        }
