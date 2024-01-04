-- Deploy gawpo-db:lang to pg
-- requires: schema
-- requires: history
BEGIN;

CREATE TABLE gwapese.lang (
  lang_tag text UNIQUE NOT NULL,
  CONSTRAINT lang_pk PRIMARY KEY (lang_tag)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'lang');

CREATE TABLE gwapese.historical_lang (
  LIKE gwapese.lang
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'lang', 'historical_lang');

CREATE TABLE gwapese.app (
  app_name text UNIQUE NOT NULL,
  CONSTRAINT app_pk PRIMARY KEY (app_name)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'app');

CREATE TABLE gwapese.historical_app (
  LIKE gwapese.app
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'app', 'historical_app');

CREATE TABLE gwapese.operating_lang (
  app_name text UNIQUE NOT NULL,
  lang_tag text NOT NULL,
  CONSTRAINT operating_lang_pk PRIMARY KEY (app_name, lang_tag),
  CONSTRAINT app_operates_operating_lang_fk FOREIGN KEY (app_name) REFERENCES
    gwapese.app (app_name) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT lang_comprises_operating_lang_fk FOREIGN KEY (lang_tag) REFERENCES
    gwapese.lang (lang_tag) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'operating_lang');

CREATE TABLE gwapese.historical_operating_lang (
  LIKE gwapese.operating_lang
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'operating_lang', 'historical_operating_lang');

CREATE TABLE gwapese.operating_copy (
  app_name text NOT NULL,
  lang_tag text NOT NULL,
  original text NOT NULL,
  CONSTRAINT operating_copy_pk PRIMARY KEY (app_name, lang_tag, original),
  CONSTRAINT operating_lang_specifies_operating_copy_fk FOREIGN KEY (app_name,
    lang_tag) REFERENCES gwapese.operating_lang (app_name, lang_tag) ON DELETE
    CASCADE ON UPDATE RESTRICT
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'operating_copy');

CREATE TABLE gwapese.historical_operating_copy (
  LIKE gwapese.operating_copy
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'operating_copy', 'historical_operating_copy');

CREATE TABLE gwapese.translated_copy (
  app_name text NOT NULL,
  original_lang_tag text NOT NULL,
  original text NOT NULL,
  translation_lang_tag text NOT NULL,
  translation text,
  CONSTRAINT translated_copy_pk PRIMARY KEY (app_name, original_lang_tag,
    original, translation_lang_tag),
  CONSTRAINT lang_comprises_translated_copy_fk FOREIGN KEY
    (translation_lang_tag) REFERENCES gwapese.lang (lang_tag) ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT operating_copy_originates_translated_copy_fk FOREIGN KEY
    (app_name, original_lang_tag, original) REFERENCES gwapese.operating_copy
    (app_name, lang_tag, original) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'translated_copy');

CREATE TABLE gwapese.historical_translated_copy (
  LIKE gwapese.translated_copy
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'translated_copy', 'historical_translated_copy');

-- CREATE OR REPLACE PROCEDURE gwapese.delete_operating_copy (IN in_app_name text,
--   IN in_lang_tag text, IN in_original text)
--   AS $$
-- BEGIN
--   DELETE FROM gwapese.operating_copy
--   WHERE app_name = in_app_name
--     AND lang_tag = in_lang_tag
--     AND original = in_original;
-- END;
-- $$
-- LANGUAGE plpgsql;
-- CREATE OR REPLACE PROCEDURE gwapese.delete_translated_copy (IN in_app_name
--   text, IN in_original_lang_tag text, IN in_original text, IN
--   in_translation_lang_tag text)
--   AS $$
-- BEGIN
--   DELETE FROM gwapese.translated_copy
--   WHERE app_name = in_app_name
--     AND original_lang_tag = in_original_lang_tag
--     AND original = in_original
--     AND translation_lang_tag = in_translation_lang_tag;
-- END;
-- $$
-- LANGUAGE plpgsql;
-- CREATE OR REPLACE PROCEDURE gwapese.upsert_operating_copy (IN in_app_name text,
--   IN in_lang_tag text, IN in_original text)
--   AS $$
-- BEGIN
--   MERGE INTO gwapese.operating_copy AS target_operating_copy
--   USING (
--   VALUES (in_app_name, in_lang_tag, in_original)) AS source_operating_copy
--     (app_name, lang_tag, original) ON target_operating_copy.app_name =
--     source_operating_copy.app_name
--     AND target_operating_copy.lang_tag = source_operating_copy.lang_tag
--     AND target_operating_copy.original = source_operating_copy.original
--   WHEN NOT MATCHED THEN
--     INSERT (app_name, lang_tag, original)
--       VALUES (source_operating_copy.app_name, source_operating_copy.lang_tag,
-- 	source_operating_copy.original);
-- END;
-- $$
-- LANGUAGE plpgsql;
-- CREATE OR REPLACE PROCEDURE gwapese.upsert_translated_copy (IN in_app_name
--   text, IN in_original_lang_tag text, IN in_original text, IN
--   in_translation_lang_tag text, IN in_translation text)
--   AS $$
-- BEGIN
--   MERGE INTO gwapese.translated_copy AS target_translated_copy
--   USING (
--   VALUES (in_app_name, in_original_lang_tag, in_original,
--     in_translation_lang_tag)) AS source_translated_copy (app_name,
--     original_lang_tag, original, translation_lang_tag) ON
--     target_translated_copy.app_name = source_translated_copy.app_name
--     AND target_translated_copy.original_lang_tag = source_translated_copy.original_lang_tag
--     AND target_translated_copy.original = source_translated_copy.original
--     AND target_translated_copy.translation_lang_tag =
--       source_translated_copy.translation_lang_tag
--   WHEN MATCHED
--     AND target_translated_copy.translation != in_translation THEN
--     UPDATE SET
--       translation = in_translation
--   WHEN NOT MATCHED THEN
--     INSERT (app_name, original_lang_tag, original, translation_lang_tag, translation)
--       VALUES (source_translated_copy.app_name,
-- 	source_translated_copy.original_lang_tag,
-- 	source_translated_copy.original,
-- 	source_translated_copy.translation_lang_tag, in_translation);
-- END;
-- $$
-- LANGUAGE plpgsql;
COMMIT;
