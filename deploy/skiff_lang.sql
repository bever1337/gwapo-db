-- Deploy gwapo-db:skiff_lang to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: skiff
BEGIN;

CREATE TABLE gwapese.skiff_name (
  LIKE gwapese.copy_source,
  skiff_id integer NOT NULL,
  CONSTRAINT skiff_name_pk PRIMARY KEY (app_name, lang_tag, skiff_id),
  CONSTRAINT skiff_identifies_name_fk FOREIGN KEY (skiff_id) REFERENCES
    gwapese.skiff (skiff_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_source_identifies_skiff_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.copy_source (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.skiff_name_history (
  LIKE gwapese.skiff_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skiff_name', 'skiff_name_history');

CREATE TABLE gwapese.skiff_name_context (
  LIKE gwapese.copy_target,
  skiff_id integer NOT NULL,
  CONSTRAINT skiff_name_context_pk PRIMARY KEY (app_name, original_lang_tag,
    skiff_id, translation_lang_tag),
  CONSTRAINT skiff_name_sources_context_fk FOREIGN KEY (app_name,
    original_lang_tag, skiff_id) REFERENCES gwapese.skiff_name (app_name,
    lang_tag, skiff_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_target_identifies_skiff_name_context_fk FOREIGN KEY
    (app_name, original_lang_tag, original, translation_lang_tag, translation)
    REFERENCES gwapese.copy_target (app_name, original_lang_tag, original,
    translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.skiff_name_context_history (
  LIKE gwapese.skiff_name_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skiff_name_context', 'skiff_name_context_history');

COMMIT;
