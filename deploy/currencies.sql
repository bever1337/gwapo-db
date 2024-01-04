-- Deploy gawpo-db:currencies to pg
-- requires: schema
-- requires: history
-- requires: lang
BEGIN;

CREATE TABLE gwapese.currency (
  currency_id smallint NOT NULL,
  deprecated boolean NOT NULL,
  icon text NOT NULL,
  presentation_order smallint NOT NULL,
  CONSTRAINT currency_pk PRIMARY KEY (currency_id)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'currency');

CREATE TABLE gwapese.historical_currency (
  LIKE gwapese.currency
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'currency', 'historical_currency');

CREATE TABLE gwapese.currency_category (
  category smallint NOT NULL,
  currency_id smallint NOT NULL,
  CONSTRAINT currency_category_pk PRIMARY KEY (currency_id, category),
  CONSTRAINT currency_has_category_fk FOREIGN KEY (currency_id) REFERENCES
    gwapese.currency (currency_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'currency_category');

CREATE TABLE gwapese.historical_currency_category (
  LIKE gwapese.currency_category
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'currency_category', 'historical_currency_category');

CREATE TABLE gwapese.currency_description (
  app_name text NOT NULL,
  currency_id smallint NOT NULL,
  lang_tag text NOT NULL,
  original text NOT NULL,
  CONSTRAINT currency_description_pk PRIMARY KEY (app_name, lang_tag, currency_id),
  CONSTRAINT currency_identifies_currency_description_fk FOREIGN KEY
    (currency_id) REFERENCES gwapese.currency (currency_id) ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT operating_copy_precedes_currency_description_fk FOREIGN KEY
    (app_name, lang_tag, original) REFERENCES gwapese.operating_copy (app_name,
    lang_tag, original) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'currency_description');

CREATE TABLE gwapese.historical_currency_description (
  LIKE gwapese.currency_description
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'currency_description', 'historical_currency_description');

CREATE TABLE gwapese.currency_name (
  app_name text NOT NULL,
  currency_id smallint NOT NULL,
  lang_tag text NOT NULL,
  original text,
  CONSTRAINT currency_name_pk PRIMARY KEY (app_name, lang_tag, currency_id),
  CONSTRAINT currency_identifies_currency_name_fk FOREIGN KEY (currency_id)
    REFERENCES gwapese.currency (currency_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT operating_copy_precedes_currency_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.operating_copy (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE RESTRICT
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'currency_name');

CREATE TABLE gwapese.historical_currency_name (
  LIKE gwapese.currency_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'currency_name', 'historical_currency_name');

-- CREATE OR REPLACE PROCEDURE gwapese.upsert_currency (IN in_currency_id
--   smallint, IN in_deprecated boolean, IN in_icon text, IN in_presentation_order
--   smallint)
--   AS $$
-- BEGIN
--   MERGE INTO gwapese.currency AS target_currency
--   USING (
--   VALUES (in_currency_id, in_deprecated, in_icon, in_presentation_order)) AS
--     source_currency (currency_id, deprecated, icon, presentation_order) ON
--     target_currency.currency_id = source_currency.currency_id
--   WHEN MATCHED
--     AND source_currency IS DISTINCT FROM (target_currency.currency_id,
--       target_currency.deprecated, target_currency.icon,
--       target_currency.presentation_order) THEN
--     UPDATE SET
--       (deprecated, icon, presentation_order) = (in_deprecated, in_icon, in_presentation_order)
--   WHEN NOT MATCHED THEN
--     INSERT (currency_id, deprecated, icon, presentation_order)
--       VALUES (in_currency_id, in_deprecated, in_icon, in_presentation_order);
-- END;
-- $$
-- LANGUAGE plpgsql;
-- CREATE OR REPLACE PROCEDURE gwapese.upsert_currency_categories (IN
--   in_currency_id smallint, IN in_categories smallint[])
--   AS $$
-- BEGIN
--   DELETE FROM gwapese.currency_category
--   WHERE currency_id = in_currency_id
--     AND NOT category = ANY (in_categories);
--   MERGE INTO gwapese.currency_category AS target_currency_category
--   USING (
--     SELECT
--       in_currency_id AS currency_id, category
--     FROM
--       UNNEST(in_categories) AS category) AS source_currency_category ON
-- 	target_currency_category.category = source_currency_category.category
--     AND target_currency_category.currency_id = source_currency_category.currency_id
--   WHEN NOT MATCHED THEN
--     INSERT (category, currency_id)
--       VALUES (source_currency_category.category, source_currency_category.currency_id);
-- END;
-- $$
-- LANGUAGE plpgsql;
-- CREATE OR REPLACE PROCEDURE gwapese.upsert_currency_description (IN in_app_name
--   text, IN in_currency_id smallint, IN in_original text, IN in_lang_tag text)
--   AS $$
-- BEGIN
--   MERGE INTO gwapese.currency_description AS target_currency_description
--   USING (
--   VALUES (in_app_name, in_currency_id, in_lang_tag, in_original)) AS
--     source_currency_description (app_name, currency_id, lang_tag, original) ON
--     target_currency_description.app_name = source_currency_description.app_name
--     AND target_currency_description.lang_tag = source_currency_description.lang_tag
--     AND target_currency_description.currency_id = source_currency_description.currency_id
--   WHEN MATCHED
--     AND target_currency_description.original != source_currency_description.original THEN
--     UPDATE SET
--       original = source_currency_description.original
--   WHEN NOT MATCHED THEN
--     INSERT (app_name, currency_id, lang_tag, original)
--       VALUES (source_currency_description.app_name,
-- 	source_currency_description.currency_id,
-- 	source_currency_description.lang_tag,
-- 	source_currency_description.original);
-- END;
-- $$
-- LANGUAGE plpgsql;
-- gwapese.upsert_operating_copy (IN in_app_name text,
--   IN in_lang_tag text, IN in_original text)
-- gwapese.upsert_translated_copy (IN in_app_name
--   text, IN in_original_lang_tag text, IN in_original text, IN
--   in_translation_lang_tag text, IN in_translation text)
COMMIT;
