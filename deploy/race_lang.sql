-- Deploy gwapo-db:race_lang to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: race
BEGIN;

CREATE TABLE gwapese.race_name (
  LIKE gwapese.copy_source,
  race_id text NOT NULL,
  CONSTRAINT race_name_pk PRIMARY KEY (app_name, lang_tag, original, race_id),
  CONSTRAINT race_name_u UNIQUE (app_name, lang_tag, race_id),
  CONSTRAINT race_identifies_name_fk FOREIGN KEY (race_id) REFERENCES
    gwapese.race (race_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_source_identifies_currency_description_fk FOREIGN KEY
    (app_name, lang_tag, original) REFERENCES gwapese.copy_source (app_name,
    lang_tag, original) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.race_name_history (
  LIKE gwapese.race_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'race_name', 'race_name_history');

CREATE TABLE gwapese.race_name_context (
  LIKE gwapese.copy_target,
  race_id text NOT NULL,
  CONSTRAINT race_name_context_pk PRIMARY KEY (app_name, original_lang_tag,
    translation_lang_tag, race_id),
  CONSTRAINT race_name_sources_context_fk FOREIGN KEY (app_name,
    original_lang_tag, original, race_id) REFERENCES gwapese.race_name
    (app_name, lang_tag, original, race_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT copy_target_identifies_race_name_context_fk FOREIGN KEY (app_name,
    original_lang_tag, original, translation_lang_tag, translation) REFERENCES
    gwapese.copy_target (app_name, original_lang_tag, original,
    translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.race_name_context_history (
  LIKE gwapese.race_name_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'race_name_context', 'race_name_context_history');

COMMIT;
