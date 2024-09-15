import luigi
from psycopg import sql

import common
import item_transform_csv
import lang_load
import profession_load_csv
import race_load_csv
from tasks import config
from tasks import load_csv

merge_into_item_reference = sql.SQL(
    """
MERGE INTO gwapese.{cross_table_name} AS target_item_reference
USING (
  SELECT
    {pk_name},
    item_id
  FROM
    {temp_table_name}
  WHERE
    EXISTS (
      SELECT
        1
      FROM
        gwapese.{table_name}
      WHERE
        gwapese.{table_name}.{pk_name} = {temp_table_name}.{pk_name})
    AND EXISTS (
      SELECT
        1
      FROM
        gwapese.item
      WHERE
        gwapese.item.item_id = {temp_table_name}.item_id)
) AS source_item_reference ON target_item_reference.{pk_name} = source_item_reference.{pk_name}
  AND target_item_reference.item_id = source_item_reference.item_id
WHEN NOT MATCHED THEN
  INSERT ({pk_name}, item_id)
    VALUES (source_item_reference.{pk_name}, source_item_reference.item_id);
"""
)


class WrapItem(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvItem(**args)
        yield LoadCsvItemDescription(**args)
        yield LoadCsvItemFlag(**args)
        yield LoadCsvItemGameType(**args)
        yield LoadCsvItemName(**args)
        yield LoadCsvItemRestrictionProfession(**args)
        yield LoadCsvItemRestrictionRace(**args)
        yield LoadCsvItemUpgrade(**args)


class WrapItemTranslate(luigi.WrapperTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        for lang_tag in common.LangTag:
            if lang_tag == self.original_lang_tag:
                continue
            yield LoadCsvItemDescriptionTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                task_datetime=self.task_datetime,
                translation_lang_tag=lang_tag,
            )
            yield LoadCsvItemNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                task_datetime=self.task_datetime,
                translation_lang_tag=lang_tag,
            )


class LoadCsvItemTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "item"


class LoadCsvItem(LoadCsvItemTask):
    table = "item"

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
MERGE INTO
  gwapese.item_rarity
USING (
  SELECT DISTINCT ON
    (rarity)
    rarity
  FROM
    tempo_item)
AS
  item_rarity_source
ON
  gwapese.item_rarity.rarity = item_rarity_source.rarity
WHEN NOT MATCHED THEN
  INSERT (rarity)
    VALUES (item_rarity_source.rarity);
"""
            ),
            sql.SQL(
                """
MERGE INTO
  gwapese.item_type
USING (
  SELECT DISTINCT ON
    (item_type)
    item_type
  FROM
    tempo_item)
AS
  item_type_source
ON
  gwapese.item_type.item_type = item_type_source.item_type
WHEN NOT MATCHED THEN
  INSERT (item_type)
    VALUES (item_type_source.item_type);
"""
            ),
            sql.SQL(
                """
MERGE INTO
  gwapese.item
AS
  target_item
USING
  tempo_item
AS
  source_item
ON
  target_item.item_id = source_item.item_id
WHEN MATCHED AND
  source_item IS DISTINCT FROM (
    target_item.chat_link, target_item.icon,
    target_item.item_id, target_item.item_type,
    target_item.rarity, target_item.required_level,
    target_item.vendor_value) THEN
  UPDATE SET
    (chat_link, icon, item_type, rarity,
      required_level, vendor_value) = (
      source_item.chat_link, source_item.icon,
      source_item.item_type, source_item.rarity,
      source_item.required_level, source_item.vendor_value)
WHEN NOT MATCHED THEN
  INSERT (chat_link, icon, item_id, item_type,
      rarity, required_level, vendor_value)
    VALUES (source_item.chat_link, source_item.icon,
      source_item.item_id, source_item.item_type,
      source_item.rarity, source_item.required_level,
      source_item.vendor_value);
"""
            ),
        ]
    )

    def requires(self):
        return {self.table: item_transform_csv.TransformCsvItem(lang_tag=self.lang_tag)}


class LoadCsvItemDescription(lang_load.LangLoadCopySourceTask):
    id_attributes = [("item_id", sql.SQL("integer NOT NULL"))]
    table = "item_description"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "item"

    def requires(self):
        return {
            self.table: item_transform_csv.TransformCsvItemDescription(
                lang_tag=self.lang_tag
            ),
            "item": LoadCsvItem(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }


class LoadCsvItemDescriptionTranslation(lang_load.LangLoadCopyTargetTask):
    id_attributes = [("item_id", sql.SQL("integer NOT NULL"))]
    table = "item_description_context"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "item"
    widget_table = "item_description"

    def requires(self):
        return {
            self.table: item_transform_csv.TransformCsvItemDescriptionTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                translation_lang_tag=self.translation_lang_tag,
            ),
            "item_description": LoadCsvItemDescription(lang_tag=self.original_lang_tag),
        }


class LoadCsvItemFlag(LoadCsvItemTask):
    table = "item_item_flag"

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
MERGE INTO
  gwapese.item_flag
USING (
  SELECT DISTINCT ON
    (flag)
    flag
  FROM
    tempo_item_item_flag)
AS
  item_flag_source
ON
  gwapese.item_flag.flag = item_flag_source.flag
WHEN NOT MATCHED THEN
  INSERT (flag)
    VALUES (item_flag_source.flag);
"""
            ),
            sql.SQL(
                """
DELETE FROM
  gwapese.item_item_flag
WHERE NOT EXISTS (
    SELECT
      1
    FROM
      tempo_item_item_flag
    WHERE
      gwapese.item_item_flag.flag = tempo_item_item_flag.flag
      AND gwapese.item_item_flag.item_id = tempo_item_item_flag.item_id);
"""
            ),
            sql.SQL(
                """
MERGE INTO
  gwapese.item_item_flag
AS
  target_item_item_flag
USING
  tempo_item_item_flag
AS
  source_item_item_flag
ON
  target_item_item_flag.flag = source_item_item_flag.flag
    AND target_item_item_flag.item_id = source_item_item_flag.item_id
WHEN NOT MATCHED THEN
  INSERT (flag, item_id)
    VALUES (source_item_item_flag.flag, source_item_item_flag.item_id);
"""
            ),
        ]
    )

    def requires(self):
        return {
            self.table: item_transform_csv.TransformCsvItemFlag(lang_tag=self.lang_tag),
            "item": LoadCsvItem(lang_tag=self.lang_tag),
        }


class LoadCsvItemGameType(LoadCsvItemTask):
    table = "item_item_game_type"

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
MERGE INTO
  gwapese.item_game_type
USING (
  SELECT DISTINCT ON
    (game_type)
    game_type
  FROM
    tempo_item_item_game_type)
AS
  item_game_type_source
ON
  gwapese.item_game_type.game_type = item_game_type_source.game_type
WHEN NOT MATCHED THEN
  INSERT (game_type)
    VALUES (item_game_type_source.game_type);
"""
            ),
            sql.SQL(
                """
DELETE FROM
  gwapese.item_item_game_type
WHERE NOT EXISTS (
  SELECT
    1
  FROM
    tempo_item_item_game_type
  WHERE
    gwapese.item_item_game_type.game_type = tempo_item_item_game_type.game_type
      AND gwapese.item_item_game_type.item_id = tempo_item_item_game_type.item_id);
"""
            ),
            sql.SQL(
                """
MERGE INTO
  gwapese.item_item_game_type
AS
  target_item_item_game_type
USING
  tempo_item_item_game_type
AS
  source_item_item_game_type
ON
  target_item_item_game_type.game_type = source_item_item_game_type.game_type
  AND target_item_item_game_type.item_id = source_item_item_game_type.item_id
WHEN NOT MATCHED THEN
  INSERT (game_type, item_id)
    VALUES (source_item_item_game_type.game_type, source_item_item_game_type.item_id);
"""
            ),
        ]
    )

    def requires(self):
        return {
            self.table: item_transform_csv.TransformCsvItemGameType(
                lang_tag=self.lang_tag
            ),
            "item": LoadCsvItem(lang_tag=self.lang_tag),
        }


class LoadCsvItemName(lang_load.LangLoadCopySourceTask):
    id_attributes = [("item_id", sql.SQL("integer NOT NULL"))]
    table = "item_name"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "item"

    def requires(self):
        return {
            self.table: item_transform_csv.TransformCsvItemName(lang_tag=self.lang_tag),
            "item": LoadCsvItem(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }


class LoadCsvItemNameTranslation(lang_load.LangLoadCopyTargetTask):
    id_attributes = [("item_id", sql.SQL("integer NOT NULL"))]
    table = "item_name_context"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "item"
    widget_table = "item_name"

    def requires(self):
        return {
            self.table: item_transform_csv.TransformCsvItemNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                translation_lang_tag=self.translation_lang_tag,
            ),
            "item_name": LoadCsvItemName(lang_tag=self.original_lang_tag),
        }


class LoadCsvItemRestrictionProfession(LoadCsvItemTask):
    table = "item_restriction_profession"

    precopy_sql = sql.SQL(
        """
CREATE TEMPORARY TABLE tempo_item_restriction_profession (
  item_id integer NOT NULL,
  restriction_id text NOT NULL
) ON COMMIT DROP;
"""
    )

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
WITH source_item_restriction_profession AS (
  SELECT
    tempo_item_restriction_profession.item_id,
    gwapese.profession.profession_id
  FROM
    tempo_item_restriction_profession
  INNER JOIN
    gwapese.profession
  ON
    gwapese.profession.profession_id = tempo_item_restriction_profession.restriction_id
)
DELETE FROM gwapese.item_restriction_profession
WHERE EXISTS (
    SELECT
      1
    FROM
      source_item_restriction_profession
    WHERE
      gwapese.item_restriction_profession.item_id = source_item_restriction_profession.item_id
  ) AND NOT EXISTS (
    SELECT
      1
    FROM
      source_item_restriction_profession
    WHERE
      gwapese.item_restriction_profession.item_id =
        source_item_restriction_profession.item_id
      AND gwapese.item_restriction_profession.profession_id = 
        source_item_restriction_profession.profession_id);
"""
            ),
            sql.SQL(
                """
MERGE INTO gwapese.item_restriction_profession AS target_item_restriction_profession
USING (
    SELECT
      tempo_item_restriction_profession.item_id,
      gwapese.profession.profession_id
    FROM
      tempo_item_restriction_profession
    INNER JOIN
      gwapese.profession
    ON
      gwapese.profession.profession_id = tempo_item_restriction_profession.restriction_id
  ) AS source_item_restriction_profession
  ON target_item_restriction_profession.profession_id =
    source_item_restriction_profession.profession_id
  AND target_item_restriction_profession.item_id =
    source_item_restriction_profession.item_id
WHEN NOT MATCHED THEN
  INSERT (item_id, profession_id)
    VALUES (source_item_restriction_profession.item_id,
      source_item_restriction_profession.profession_id);
"""
            ),
        ]
    )

    def requires(self):
        return {
            self.table: item_transform_csv.TransformCsvItemRestriction(
                lang_tag=self.lang_tag
            ),
            "profession": profession_load_csv.LoadCsvProfession(lang_tag=self.lang_tag),
            "item": LoadCsvItem(lang_tag=self.lang_tag),
        }


class LoadCsvItemRestrictionRace(LoadCsvItemTask):
    table = "item_restriction_race"

    precopy_sql = sql.SQL(
        """
CREATE TEMPORARY TABLE tempo_item_restriction_race (
  item_id integer NOT NULL,
  restriction_id text NOT NULL
) ON COMMIT DROP;
"""
    )

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
WITH source_item_restriction_race AS (
  SELECT
    tempo_item_restriction_race.item_id,
    gwapese.race.race_id
  FROM
    tempo_item_restriction_race
  INNER JOIN
    gwapese.race
  ON
    gwapese.race.race_id = tempo_item_restriction_race.restriction_id
)
DELETE FROM gwapese.item_restriction_race
WHERE EXISTS (
    SELECT
      1
    FROM
      source_item_restriction_race
    WHERE
      gwapese.item_restriction_race.item_id = source_item_restriction_race.item_id
  ) AND NOT EXISTS (
    SELECT
      1
    FROM
      source_item_restriction_race
    WHERE
      gwapese.item_restriction_race.item_id =
        source_item_restriction_race.item_id
      AND gwapese.item_restriction_race.race_id = 
        source_item_restriction_race.race_id);
"""
            ),
            sql.SQL(
                """
MERGE INTO gwapese.item_restriction_race AS target_item_restriction_race
USING (
    SELECT
      tempo_item_restriction_race.item_id,
      gwapese.race.race_id
    FROM
      tempo_item_restriction_race
    INNER JOIN
      gwapese.race
    ON
      gwapese.race.race_id = tempo_item_restriction_race.restriction_id
  ) AS source_item_restriction_race
  ON target_item_restriction_race.race_id =
    source_item_restriction_race.race_id
  AND target_item_restriction_race.item_id =
    source_item_restriction_race.item_id
WHEN NOT MATCHED THEN
  INSERT (item_id, race_id)
    VALUES (source_item_restriction_race.item_id,
      source_item_restriction_race.race_id);
"""
            ),
        ]
    )

    def requires(self):
        return {
            self.table: item_transform_csv.TransformCsvItemRestriction(
                lang_tag=self.lang_tag
            ),
            "race": race_load_csv.LoadCsvRace(lang_tag=self.lang_tag),
            "item": LoadCsvItem(lang_tag=self.lang_tag),
        }


class LoadCsvItemUpgrade(LoadCsvItemTask):
    table = "item_upgrade"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.item_upgrade AS target_item_upgrade
USING (
  SELECT
    DISTINCT
      from_item_id, to_item_id, upgrade
    FROM
      tempo_item_upgrade
    WHERE
      EXISTS (
        SELECT
          1
        FROM
          gwapese.item
        WHERE
          gwapese.item.item_id = tempo_item_upgrade.from_item_id)
      AND EXISTS (
        SELECT
          1
        FROM
          gwapese.item
        WHERE
	      gwapese.item.item_id = tempo_item_upgrade.to_item_id)
) AS source_item_upgrade ON target_item_upgrade.from_item_id =
  source_item_upgrade.from_item_id
  AND target_item_upgrade.to_item_id = source_item_upgrade.to_item_id
  AND target_item_upgrade.upgrade = source_item_upgrade.upgrade
WHEN NOT MATCHED THEN
    INSERT
      (from_item_id, to_item_id, upgrade)
        VALUES (source_item_upgrade.from_item_id,
        source_item_upgrade.to_item_id,
	      source_item_upgrade.upgrade);
"""
    )

    def requires(self):
        return {
            self.table: item_transform_csv.TransformCsvItemUpgrade(
                lang_tag=self.lang_tag
            ),
            "item": LoadCsvItem(lang_tag=self.lang_tag),
        }
