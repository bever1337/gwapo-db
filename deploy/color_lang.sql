-- Deploy gwapo-db:color_lang to pg
-- requires: schema
-- requires: history
-- requires: lang
BEGIN;

CREATE TABLE gwapese.color_name (
  LIKE gwapese.copy_source,
  color_id integer NOT NULL,
  CONSTRAINT color_name_pk PRIMARY KEY (app_name, lang_tag, original, color_id),
  CONSTRAINT color_name_u UNIQUE (app_name, lang_tag, color_id),
  CONSTRAINT color_identifies_name_fk FOREIGN KEY (color_id) REFERENCES
    gwapese.color (color_id) ON DELETE CASCADE,
  CONSTRAINT copy_source_identifies_color_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.copy_source (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.color_name_history (
  LIKE gwapese.color_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'color_name', 'color_name_history');

CREATE TABLE gwapese.color_name_context (
  LIKE gwapese.copy_target,
  color_id integer NOT NULL,
  CONSTRAINT color_name_context_pk PRIMARY KEY (app_name, original_lang_tag,
    translation_lang_tag, color_id),
  CONSTRAINT color_name_sources_context_fk FOREIGN KEY (app_name,
    original_lang_tag, original, color_id) REFERENCES gwapese.color_name
    (app_name, lang_tag, original, color_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT copy_target_identifies_color_name_context_fk FOREIGN KEY
    (app_name, original_lang_tag, original, translation_lang_tag, translation)
    REFERENCES gwapese.copy_target (app_name, original_lang_tag, original,
    translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.color_name_context_history (
  LIKE gwapese.color_name_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'color_name_context', 'color_name_context_history');

COMMIT;
