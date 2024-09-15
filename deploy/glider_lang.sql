-- Deploy gwapo-db:glider_lang to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: glider
BEGIN;

CREATE TABLE gwapese.glider_description (
  LIKE gwapese.copy_source,
  glider_id integer NOT NULL,
  CONSTRAINT glider_description_pk PRIMARY KEY (app_name, lang_tag, glider_id),
  CONSTRAINT glider_identifies_description_fk FOREIGN KEY (glider_id)
    REFERENCES gwapese.glider (glider_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_source_identifies_glider_description_fk FOREIGN KEY
    (app_name, lang_tag, original) REFERENCES gwapese.copy_source (app_name,
    lang_tag, original) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.glider_description_history (
  LIKE gwapese.glider_description
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'glider_description', 'glider_description_history');

CREATE TABLE gwapese.glider_description_context (
  LIKE gwapese.copy_target,
  glider_id integer NOT NULL,
  CONSTRAINT glider_description_context_pk PRIMARY KEY (app_name,
    original_lang_tag, glider_id, translation_lang_tag),
  CONSTRAINT glider_description_sources_context_fk FOREIGN KEY (app_name,
    original_lang_tag, glider_id) REFERENCES gwapese.glider_description
    (app_name, lang_tag, glider_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_target_identifies_glider_description_context_fk FOREIGN KEY
    (app_name, original_lang_tag, original, translation_lang_tag, translation)
    REFERENCES gwapese.copy_target (app_name, original_lang_tag, original,
    translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.glider_description_context_history (
  LIKE gwapese.glider_description_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'glider_description_context', 'glider_description_context_history');

CREATE TABLE gwapese.glider_name (
  LIKE gwapese.copy_source,
  glider_id integer NOT NULL,
  CONSTRAINT glider_name_pk PRIMARY KEY (app_name, lang_tag, glider_id),
  CONSTRAINT glider_identifies_name_fk FOREIGN KEY (glider_id) REFERENCES
    gwapese.glider (glider_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_source_identifies_glider_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.copy_source (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.glider_name_history (
  LIKE gwapese.glider_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'glider_name', 'glider_name_history');

CREATE TABLE gwapese.glider_name_context (
  LIKE gwapese.copy_target,
  glider_id integer NOT NULL,
  CONSTRAINT glider_name_context_pk PRIMARY KEY (app_name, original_lang_tag,
    glider_id, translation_lang_tag),
  CONSTRAINT glider_name_sources_context_fk FOREIGN KEY (app_name,
    original_lang_tag, glider_id) REFERENCES gwapese.glider_name (app_name,
    lang_tag, glider_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_target_identifies_glider_name_context_fk FOREIGN KEY
    (app_name, original_lang_tag, original, translation_lang_tag, translation)
    REFERENCES gwapese.copy_target (app_name, original_lang_tag, original,
    translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.glider_name_context_history (
  LIKE gwapese.glider_name_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'glider_name_context', 'glider_name_context_history');

COMMIT;
