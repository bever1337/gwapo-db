-- Deploy gwapo-db:specialization_lang to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: specialization
BEGIN;

CREATE TABLE gwapese.specialization_name (
  LIKE gwapese.copy_source,
  specialization_id integer NOT NULL,
  CONSTRAINT specialization_name_pk PRIMARY KEY (app_name, lang_tag, specialization_id),
  CONSTRAINT specialization_identifies_name_fk FOREIGN KEY (specialization_id)
    REFERENCES gwapese.specialization (specialization_id) ON DELETE CASCADE ON
    UPDATE CASCADE,
  CONSTRAINT copy_source_identifies_specialization_name_fk FOREIGN KEY
    (app_name, lang_tag, original) REFERENCES gwapese.copy_source (app_name,
    lang_tag, original) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.specialization_name_history (
  LIKE gwapese.specialization_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'specialization_name', 'specialization_name_history');

CREATE TABLE gwapese.specialization_name_context (
  LIKE gwapese.copy_target,
  specialization_id integer NOT NULL,
  CONSTRAINT specialization_name_context_pk PRIMARY KEY (app_name,
    original_lang_tag, specialization_id, translation_lang_tag),
  CONSTRAINT specialization_name_sources_context_fk FOREIGN KEY (app_name,
    original_lang_tag, specialization_id) REFERENCES
    gwapese.specialization_name (app_name, lang_tag, specialization_id) ON
    DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_target_identifies_specialization_name_context_fk FOREIGN KEY
    (app_name, original_lang_tag, original, translation_lang_tag, translation)
    REFERENCES gwapese.copy_target (app_name, original_lang_tag, original,
    translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.specialization_name_context_history (
  LIKE gwapese.specialization_name_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'specialization_name_context', 'specialization_name_context_history');

COMMIT;
