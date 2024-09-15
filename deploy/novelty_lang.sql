-- Deploy gwapo-db:novelty_lang to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: novelty
BEGIN;

CREATE TABLE gwapese.novelty_description (
  LIKE gwapese.copy_source,
  novelty_id integer NOT NULL,
  CONSTRAINT novelty_description_pk PRIMARY KEY (app_name, lang_tag, novelty_id),
  CONSTRAINT novelty_identifies_description_fk FOREIGN KEY (novelty_id)
    REFERENCES gwapese.novelty (novelty_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT copy_source_identifies_novelty_description_fk FOREIGN KEY
    (app_name, lang_tag, original) REFERENCES gwapese.copy_source (app_name,
    lang_tag, original) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.novelty_description_history (
  LIKE gwapese.novelty_description
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'novelty_description', 'novelty_description_history');

CREATE TABLE gwapese.novelty_description_context (
  LIKE gwapese.copy_target,
  novelty_id integer NOT NULL,
  CONSTRAINT novelty_description_context_pk PRIMARY KEY (app_name,
    original_lang_tag, novelty_id, translation_lang_tag),
  CONSTRAINT novelty_description_sources_context_fk FOREIGN KEY (app_name,
    original_lang_tag, novelty_id) REFERENCES gwapese.novelty_description
    (app_name, lang_tag, novelty_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_target_identifies_novelty_description_context_fk FOREIGN KEY
    (app_name, original_lang_tag, original, translation_lang_tag, translation)
    REFERENCES gwapese.copy_target (app_name, original_lang_tag, original,
    translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.novelty_description_context_history (
  LIKE gwapese.novelty_description_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'novelty_description_context', 'novelty_description_context_history');

CREATE TABLE gwapese.novelty_name (
  LIKE gwapese.copy_source,
  novelty_id integer NOT NULL,
  CONSTRAINT novelty_name_pk PRIMARY KEY (app_name, lang_tag, novelty_id),
  CONSTRAINT novelty_identifies_name_fk FOREIGN KEY (novelty_id) REFERENCES
    gwapese.novelty (novelty_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_source_identifies_novelty_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.copy_source (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.novelty_name_history (
  LIKE gwapese.novelty_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'novelty_name', 'novelty_name_history');

CREATE TABLE gwapese.novelty_name_context (
  LIKE gwapese.copy_target,
  novelty_id integer NOT NULL,
  CONSTRAINT novelty_name_context_pk PRIMARY KEY (app_name, original_lang_tag,
    novelty_id, translation_lang_tag),
  CONSTRAINT novelty_name_sources_context_fk FOREIGN KEY (app_name,
    original_lang_tag, novelty_id) REFERENCES gwapese.novelty_name (app_name,
    lang_tag, novelty_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_target_identifies_novelty_name_context_fk FOREIGN KEY
    (app_name, original_lang_tag, original, translation_lang_tag, translation)
    REFERENCES gwapese.copy_target (app_name, original_lang_tag, original,
    translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.novelty_name_context_history (
  LIKE gwapese.novelty_name_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'novelty_name_context', 'novelty_name_context_history');

COMMIT;
