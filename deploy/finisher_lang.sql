-- Deploy gwapo-db:finisher_lang to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: finisher
BEGIN;

CREATE TABLE gwapese.finisher_detail (
  LIKE gwapese.copy_source,
  finisher_id integer NOT NULL,
  CONSTRAINT finisher_detail_pk PRIMARY KEY (app_name, lang_tag, original, finisher_id),
  CONSTRAINT finisher_detail_u UNIQUE (app_name, lang_tag, finisher_id),
  CONSTRAINT finisher_identifies_detail_fk FOREIGN KEY (finisher_id) REFERENCES
    gwapese.finisher (finisher_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_source_identifies_finisher_detail_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.copy_source (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.finisher_detail_history (
  LIKE gwapese.finisher_detail
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'finisher_detail', 'finisher_detail_history');

CREATE TABLE gwapese.finisher_detail_context (
  LIKE gwapese.copy_target,
  finisher_id integer NOT NULL,
  CONSTRAINT finisher_detail_context_pk PRIMARY KEY (app_name,
    original_lang_tag, translation_lang_tag, finisher_id),
  CONSTRAINT finisher_detail_sources_context_fk FOREIGN KEY (app_name,
    original_lang_tag, original, finisher_id) REFERENCES
    gwapese.finisher_detail (app_name, lang_tag, original, finisher_id) ON
    DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_target_identifies_finisher_detail_context_fk FOREIGN KEY
    (app_name, original_lang_tag, original, translation_lang_tag, translation)
    REFERENCES gwapese.copy_target (app_name, original_lang_tag, original,
    translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.finisher_detail_context_history (
  LIKE gwapese.finisher_detail_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'finisher_detail_context', 'finisher_detail_context_history');

CREATE TABLE gwapese.finisher_name (
  LIKE gwapese.copy_source,
  finisher_id integer NOT NULL,
  CONSTRAINT finisher_name_pk PRIMARY KEY (app_name, lang_tag, original, finisher_id),
  CONSTRAINT finisher_name_u UNIQUE (app_name, lang_tag, finisher_id),
  CONSTRAINT finisher_identifies_name_fk FOREIGN KEY (finisher_id) REFERENCES
    gwapese.finisher (finisher_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_source_identifies_finisher_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.copy_source (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.finisher_name_history (
  LIKE gwapese.finisher_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'finisher_name', 'finisher_name_history');

CREATE TABLE gwapese.finisher_name_context (
  LIKE gwapese.copy_target,
  finisher_id integer NOT NULL,
  CONSTRAINT finisher_name_context_pk PRIMARY KEY (app_name, original_lang_tag,
    translation_lang_tag, finisher_id),
  CONSTRAINT finisher_name_sources_context_fk FOREIGN KEY (app_name,
    original_lang_tag, original, finisher_id) REFERENCES gwapese.finisher_name
    (app_name, lang_tag, original, finisher_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT copy_target_identifies_finisher_name_context_fk FOREIGN KEY
    (app_name, original_lang_tag, original, translation_lang_tag, translation)
    REFERENCES gwapese.copy_target (app_name, original_lang_tag, original,
    translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.finisher_name_context_history (
  LIKE gwapese.finisher_name_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'finisher_name_context', 'finisher_name_context_history');

COMMIT;
