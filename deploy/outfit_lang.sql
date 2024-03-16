-- Deploy gwapo-db:outfit_lang to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: outfit
BEGIN;

CREATE TABLE gwapese.outfit_name (
  LIKE gwapese.copy_source,
  outfit_id integer NOT NULL,
  CONSTRAINT outfit_name_pk PRIMARY KEY (app_name, lang_tag, original, outfit_id),
  CONSTRAINT outfit_name_u UNIQUE (app_name, lang_tag, outfit_id),
  CONSTRAINT outfit_identifies_name_fk FOREIGN KEY (outfit_id) REFERENCES
    gwapese.outfit (outfit_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_source_identifies_outfit_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.copy_source (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.outfit_name_history (
  LIKE gwapese.outfit_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'outfit_name', 'outfit_name_history');

CREATE TABLE gwapese.outfit_name_context (
  LIKE gwapese.copy_target,
  outfit_id integer NOT NULL,
  CONSTRAINT outfit_name_context_pk PRIMARY KEY (app_name, original_lang_tag,
    translation_lang_tag, outfit_id),
  CONSTRAINT outfit_name_sources_context_fk FOREIGN KEY (app_name,
    original_lang_tag, original, outfit_id) REFERENCES gwapese.outfit_name
    (app_name, lang_tag, original, outfit_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT copy_target_identifies_outfit_name_context_fk FOREIGN KEY
    (app_name, original_lang_tag, original, translation_lang_tag, translation)
    REFERENCES gwapese.copy_target (app_name, original_lang_tag, original,
    translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.outfit_name_context_history (
  LIKE gwapese.outfit_name_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'outfit_name_context', 'outfit_name_context_history');

COMMIT;
