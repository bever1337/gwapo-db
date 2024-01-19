-- Deploy gawpo-db:lang to pg
-- requires: schema
-- requires: history
BEGIN;

CREATE TABLE gwapese.lang (
  lang_tag text UNIQUE NOT NULL,
  CONSTRAINT lang_pk PRIMARY KEY (lang_tag)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'lang');

CREATE TABLE gwapese.lang_history (
  LIKE gwapese.lang
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'lang', 'lang_history');

CREATE TABLE gwapese.app (
  app_name text UNIQUE NOT NULL,
  CONSTRAINT app_pk PRIMARY KEY (app_name)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'app');

CREATE TABLE gwapese.app_history (
  LIKE gwapese.app
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'app', 'app_history');

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

CREATE TABLE gwapese.operating_lang_history (
  LIKE gwapese.operating_lang
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'operating_lang', 'operating_lang_history');

CREATE TABLE gwapese.operating_copy (
  app_name text NOT NULL,
  lang_tag text NOT NULL,
  original text NOT NULL,
  CONSTRAINT operating_copy_pk PRIMARY KEY (app_name, lang_tag, original),
  CONSTRAINT operating_lang_specifies_operating_copy_fk FOREIGN KEY (app_name,
    lang_tag) REFERENCES gwapese.operating_lang (app_name, lang_tag) ON DELETE
    CASCADE ON UPDATE RESTRICT,
  CONSTRAINT original_not_empty_ck CHECK (original <> '')
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'operating_copy');

CREATE TABLE gwapese.operating_copy_history (
  LIKE gwapese.operating_copy
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'operating_copy', 'operating_copy_history');

CREATE TABLE gwapese.translated_copy (
  app_name text NOT NULL,
  original_lang_tag text NOT NULL,
  original text NOT NULL,
  translation_lang_tag text NOT NULL,
  translation text NOT NULL,
  CONSTRAINT translated_copy_pk PRIMARY KEY (app_name, original_lang_tag,
    original, translation_lang_tag),
  CONSTRAINT lang_comprises_translated_copy_fk FOREIGN KEY
    (translation_lang_tag) REFERENCES gwapese.lang (lang_tag) ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT operating_copy_originates_translated_copy_fk FOREIGN KEY
    (app_name, original_lang_tag, original) REFERENCES gwapese.operating_copy
    (app_name, lang_tag, original) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT translation_not_empty_ck CHECK (translation <> '')
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'translated_copy');

CREATE TABLE gwapese.translated_copy_history (
  LIKE gwapese.translated_copy
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'translated_copy', 'translated_copy_history');

COMMIT;
