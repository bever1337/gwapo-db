-- Deploy gwapo-db:mini_lang to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: mini
BEGIN;

CREATE TABLE gwapese.mini_name (
  LIKE gwapese.copy_source,
  mini_id integer NOT NULL,
  CONSTRAINT mini_name_pk PRIMARY KEY (app_name, lang_tag, original, mini_id),
  CONSTRAINT mini_name_u UNIQUE (app_name, lang_tag, mini_id),
  CONSTRAINT mini_identifies_name_fk FOREIGN KEY (mini_id) REFERENCES
    gwapese.mini (mini_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_source_identifies_mini_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.copy_source (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.mini_name_history (
  LIKE gwapese.mini_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'mini_name', 'mini_name_history');

CREATE TABLE gwapese.mini_name_context (
  LIKE gwapese.copy_target,
  mini_id integer NOT NULL,
  CONSTRAINT mini_name_context_pk PRIMARY KEY (app_name, original_lang_tag,
    translation_lang_tag, mini_id),
  CONSTRAINT mini_name_sources_context_fk FOREIGN KEY (app_name,
    original_lang_tag, original, mini_id) REFERENCES gwapese.mini_name
    (app_name, lang_tag, original, mini_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT copy_target_identifies_mini_name_context_fk FOREIGN KEY (app_name,
    original_lang_tag, original, translation_lang_tag, translation) REFERENCES
    gwapese.copy_target (app_name, original_lang_tag, original,
    translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.mini_name_context_history (
  LIKE gwapese.mini_name_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'mini_name_context', 'mini_name_context_history');

CREATE TABLE gwapese.mini_unlock (
  LIKE gwapese.copy_source,
  mini_id integer NOT NULL,
  CONSTRAINT mini_unlock_pk PRIMARY KEY (app_name, lang_tag, original, mini_id),
  CONSTRAINT mini_unlock_u UNIQUE (app_name, lang_tag, mini_id),
  CONSTRAINT mini_identifies_unlock_fk FOREIGN KEY (mini_id) REFERENCES
    gwapese.mini (mini_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_source_identifies_mini_unlock_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.copy_source (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.mini_unlock_history (
  LIKE gwapese.mini_unlock
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'mini_unlock', 'mini_unlock_history');

CREATE TABLE gwapese.mini_unlock_context (
  LIKE gwapese.copy_target,
  mini_id integer NOT NULL,
  CONSTRAINT mini_unlock_context_pk PRIMARY KEY (app_name, original_lang_tag,
    translation_lang_tag, mini_id),
  CONSTRAINT mini_unlock_sources_context_fk FOREIGN KEY (app_name,
    original_lang_tag, original, mini_id) REFERENCES gwapese.mini_unlock
    (app_name, lang_tag, original, mini_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT copy_target_identifies_mini_unlock_context_fk FOREIGN KEY
    (app_name, original_lang_tag, original, translation_lang_tag, translation)
    REFERENCES gwapese.copy_target (app_name, original_lang_tag, original,
    translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.mini_unlock_context_history (
  LIKE gwapese.mini_unlock_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'mini_unlock_context', 'mini_unlock_context_history');

COMMIT;
