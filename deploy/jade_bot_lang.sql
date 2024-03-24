-- Deploy gwapo-db:jade_bot_lang to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: jade_bot
BEGIN;

CREATE TABLE gwapese.jade_bot_description (
  LIKE gwapese.copy_source,
  jade_bot_id integer NOT NULL,
  CONSTRAINT jade_bot_description_pk PRIMARY KEY (app_name, lang_tag, original,
    jade_bot_id),
  CONSTRAINT jade_bot_description_u UNIQUE (app_name, lang_tag, jade_bot_id),
  CONSTRAINT jade_bot_identifies_description_fk FOREIGN KEY (jade_bot_id)
    REFERENCES gwapese.jade_bot (jade_bot_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT copy_source_identifies_jade_bot_description_fk FOREIGN KEY
    (app_name, lang_tag, original) REFERENCES gwapese.copy_source (app_name,
    lang_tag, original) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.jade_bot_description_history (
  LIKE gwapese.jade_bot_description
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'jade_bot_description', 'jade_bot_description_history');

CREATE TABLE gwapese.jade_bot_description_context (
  LIKE gwapese.copy_target,
  jade_bot_id integer NOT NULL,
  CONSTRAINT jade_bot_description_context_pk PRIMARY KEY (app_name,
    original_lang_tag, translation_lang_tag, jade_bot_id),
  CONSTRAINT jade_bot_description_sources_context_fk FOREIGN KEY (app_name,
    original_lang_tag, original, jade_bot_id) REFERENCES
    gwapese.jade_bot_description (app_name, lang_tag, original, jade_bot_id) ON
    DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_target_identifies_jade_bot_description_context_fk FOREIGN KEY
    (app_name, original_lang_tag, original, translation_lang_tag, translation)
    REFERENCES gwapese.copy_target (app_name, original_lang_tag, original,
    translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.jade_bot_description_context_history (
  LIKE gwapese.jade_bot_description_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'jade_bot_description_context', 'jade_bot_description_context_history');

CREATE TABLE gwapese.jade_bot_name (
  LIKE gwapese.copy_source,
  jade_bot_id integer NOT NULL,
  CONSTRAINT jade_bot_name_pk PRIMARY KEY (app_name, lang_tag, original, jade_bot_id),
  CONSTRAINT jade_bot_name_u UNIQUE (app_name, lang_tag, jade_bot_id),
  CONSTRAINT jade_bot_identifies_name_fk FOREIGN KEY (jade_bot_id) REFERENCES
    gwapese.jade_bot (jade_bot_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_source_identifies_jade_bot_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.copy_source (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.jade_bot_name_history (
  LIKE gwapese.jade_bot_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'jade_bot_name', 'jade_bot_name_history');

CREATE TABLE gwapese.jade_bot_name_context (
  LIKE gwapese.copy_target,
  jade_bot_id integer NOT NULL,
  CONSTRAINT jade_bot_name_context_pk PRIMARY KEY (app_name, original_lang_tag,
    translation_lang_tag, jade_bot_id),
  CONSTRAINT jade_bot_name_sources_context_fk FOREIGN KEY (app_name,
    original_lang_tag, original, jade_bot_id) REFERENCES gwapese.jade_bot_name
    (app_name, lang_tag, original, jade_bot_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT copy_target_identifies_jade_bot_name_context_fk FOREIGN KEY
    (app_name, original_lang_tag, original, translation_lang_tag, translation)
    REFERENCES gwapese.copy_target (app_name, original_lang_tag, original,
    translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.jade_bot_name_context_history (
  LIKE gwapese.jade_bot_name_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'jade_bot_name_context', 'jade_bot_name_context_history');

COMMIT;
