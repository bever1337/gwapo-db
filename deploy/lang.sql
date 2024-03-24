-- Deploy gwapo-db:lang to pg
-- requires: schema
-- requires: history
BEGIN;

CREATE TABLE gwapese.lang (
  lang_tag text UNIQUE NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT lang_pk PRIMARY KEY (lang_tag)
);

CREATE TABLE gwapese.lang_history (
  LIKE gwapese.lang
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'lang', 'lang_history');

CREATE TABLE gwapese.app (
  app_name text NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT app_pk PRIMARY KEY (app_name)
);

CREATE TABLE gwapese.app_history (
  LIKE gwapese.app
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'app', 'app_history');

CREATE TABLE gwapese.copy_document (
  app_name text NOT NULL,
  document xml GENERATED ALWAYS AS (XMLPARSE (CONTENT original)) STORED NOT NULL,
  lang_tag text NOT NULL,
  original text NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT copy_document_pk PRIMARY KEY (app_name, lang_tag, original),
  CONSTRAINT lang_comprises_copy_document FOREIGN KEY (lang_tag) REFERENCES
    gwapese.lang (lang_tag) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.copy_document_history (
  LIKE gwapese.copy_document
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'copy_document', 'copy_document_history');

CREATE TABLE gwapese.operating_lang (
  app_name text NOT NULL,
  lang_tag text NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT operating_lang_pk PRIMARY KEY (app_name, lang_tag),
  CONSTRAINT app_operates_operating_lang_fk FOREIGN KEY (app_name) REFERENCES
    gwapese.app (app_name) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT lang_comprises_operating_lang_fk FOREIGN KEY (lang_tag) REFERENCES
    gwapese.lang (lang_tag) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.operating_lang_history (
  LIKE gwapese.operating_lang
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'operating_lang', 'operating_lang_history');

CREATE TABLE gwapese.copy_source (
  app_name text NOT NULL,
  lang_tag text NOT NULL,
  original text NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT copy_source_pk PRIMARY KEY (app_name, lang_tag, original),
  CONSTRAINT copy_document_identifies_copy_source_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.copy_document (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT operating_lang_specifies_copy_source_fk FOREIGN KEY (app_name,
    lang_tag) REFERENCES gwapese.operating_lang (app_name, lang_tag) ON DELETE
    CASCADE ON UPDATE RESTRICT
);

CREATE TABLE gwapese.copy_source_history (
  LIKE gwapese.copy_source
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'copy_source', 'copy_source_history');

CREATE TABLE gwapese.copy_target (
  app_name text NOT NULL,
  original_lang_tag text NOT NULL,
  original text NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  translation_lang_tag text NOT NULL,
  translation text NOT NULL,
  CONSTRAINT copy_target_pk PRIMARY KEY (app_name, original_lang_tag, original,
    translation_lang_tag, translation),
  CONSTRAINT copy_document_identifies_copy_target_fk FOREIGN KEY (app_name,
    translation_lang_tag, translation) REFERENCES gwapese.copy_document
    (app_name, lang_tag, original) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_source_originates_copy_target_fk FOREIGN KEY (app_name,
    original_lang_tag, original) REFERENCES gwapese.copy_source (app_name,
    lang_tag, original) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.copy_target_history (
  LIKE gwapese.copy_target
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'copy_target', 'copy_target_history');

COMMIT;
