import luigi
from psycopg import sql

import common
import load_csv
import load_item
import load_lang
import transform_novelty


class WrapNovelty(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        args = {"lang_tag": self.lang_tag}
        yield LoadNovelty(**args)
        yield LoadNoveltyDescription(**args)
        yield LoadNoveltyName(**args)


class LoadNoveltyTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)


class LoadNovelty(LoadNoveltyTask):
    table = "novelty"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.novelty AS target_novelty
USING tempo_novelty AS source_novelty ON target_novelty.novelty_id =
  source_novelty.novelty_id
WHEN MATCHED
  AND target_novelty.icon != source_novelty.icon
  OR target_novelty.slot != source_novelty.slot THEN
  UPDATE SET
    (icon, slot) = (source_novelty.icon, source_novelty.slot)
WHEN NOT MATCHED THEN
  INSERT (icon, novelty_id, slot)
    VALUES (source_novelty.icon, source_novelty.novelty_id, source_novelty.slot);
"""
    )

    def requires(self):
        return {self.table: transform_novelty.TransformNovelty(lang_tag=self.lang_tag)}


class LoadNoveltyDescription(LoadNoveltyTask):
    table = "novelty_description"

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_novelty_description")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("novelty_description"),
                temp_table_name=sql.Identifier("tempo_novelty_description"),
                pk_name=sql.Identifier("novelty_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: transform_novelty.TransformNoveltyDescription(
                lang_tag=self.lang_tag
            ),
            "novelty": LoadNovelty(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }


class LoadNoveltyItem(LoadNoveltyTask):
    table = "novelty_item"

    postcopy_sql = load_item.merge_into_item_reference.format(
        cross_table_name=sql.Identifier("novelty_item"),
        table_name=sql.Identifier("novelty"),
        temp_table_name=sql.Identifier("tempo_novelty_item"),
        pk_name=sql.Identifier("novelty_id"),
    )

    def requires(self):
        return {
            self.table: transform_novelty.TransformNoveltyItem(lang_tag=self.lang_tag),
            "novelty": LoadNovelty(lang_tag=self.lang_tag),
            "item": load_item.LoadItem(lang_tag=self.lang_tag),
        }


class LoadNoveltyName(LoadNoveltyTask):
    table = "novelty_name"

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_novelty_name")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("novelty_name"),
                temp_table_name=sql.Identifier("tempo_novelty_name"),
                pk_name=sql.Identifier("novelty_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: transform_novelty.TransformNoveltyName(lang_tag=self.lang_tag),
            "novelty": LoadNovelty(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }
