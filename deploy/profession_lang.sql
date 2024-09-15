-- Deploy gwapo-db:profession_lang to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: profession
BEGIN;

CREATE TABLE gwapese.profession_name (
  LIKE gwapese.copy_source,
  profession_id text NOT NULL,
  CONSTRAINT profession_name_pk PRIMARY KEY (app_name, lang_tag, profession_id),
  CONSTRAINT profession_identifies_name_fk FOREIGN KEY (profession_id)
    REFERENCES gwapese.profession (profession_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT copy_source_identifies_profession_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.copy_source (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.profession_name_history (
  LIKE gwapese.profession_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'profession_name', 'profession_name_history');

CREATE TABLE gwapese.profession_name_context (
  LIKE gwapese.copy_target,
  profession_id text NOT NULL,
  CONSTRAINT profession_name_context_pk PRIMARY KEY (app_name,
    original_lang_tag, profession_id, translation_lang_tag),
  CONSTRAINT profession_name_sources_context_fk FOREIGN KEY (app_name,
    original_lang_tag, profession_id) REFERENCES gwapese.profession_name
    (app_name, lang_tag, profession_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_target_identifies_profession_name_context_fk FOREIGN KEY
    (app_name, original_lang_tag, original, translation_lang_tag, translation)
    REFERENCES gwapese.copy_target (app_name, original_lang_tag, original,
    translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.profession_name_context_history (
  LIKE gwapese.profession_name_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'profession_name_context', 'profession_name_context_history');

COMMIT;
