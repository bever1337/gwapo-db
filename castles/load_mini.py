import luigi
from psycopg import sql

import common
import load_csv
import load_item
import load_lang
import transform_mini


class WrapMini(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        args = {"lang_tag": self.lang_tag}
        yield LoadMini(**args)
        yield LoadMiniName(**args)
        yield LoadMiniUnlock(**args)


class LoadMiniTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)


class LoadMini(LoadMiniTask):
    table = "mini"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.mini AS target_mini
USING tempo_mini AS source_mini ON target_mini.mini_id = source_mini.mini_id
WHEN MATCHED
  AND target_mini.icon != source_mini.icon
  OR target_mini.presentation_order != source_mini.presentation_order THEN
  UPDATE SET
    (icon, presentation_order) = (source_mini.icon, source_mini.presentation_order)
WHEN NOT MATCHED THEN
  INSERT (icon, mini_id, presentation_order)
    VALUES (source_mini.icon, source_mini.mini_id, source_mini.presentation_order);
"""
    )

    def requires(self):
        return {self.table: transform_mini.TransformMini(lang_tag=self.lang_tag)}


class LoadMiniItem(LoadMiniTask):
    table = "mini_item"

    postcopy_sql = load_item.merge_into_item_reference.format(
        cross_table_name=sql.Identifier("mini_item"),
        table_name=sql.Identifier("mini"),
        temp_table_name=sql.Identifier("tempo_mini_item"),
        pk_name=sql.Identifier("mini_id"),
    )

    def requires(self):
        return {
            self.table: transform_mini.TransformMiniItem(lang_tag=self.lang_tag),
            "mini": LoadMini(lang_tag=self.lang_tag),
            "item": load_item.LoadItem(lang_tag=self.lang_tag),
        }


class LoadMiniName(LoadMiniTask):
    table = "mini_name"

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_mini_name")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("mini_name"),
                temp_table_name=sql.Identifier("tempo_mini_name"),
                pk_name=sql.Identifier("mini_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: transform_mini.TransformMiniName(lang_tag=self.lang_tag),
            "mini": LoadMini(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }


class LoadMiniUnlock(LoadMiniTask):
    table = "mini_unlock"

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_mini_unlock")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("mini_unlock"),
                temp_table_name=sql.Identifier("tempo_mini_unlock"),
                pk_name=sql.Identifier("mini_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: transform_mini.TransformMiniUnlock(lang_tag=self.lang_tag),
            "mini": LoadMini(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }
