-- Deploy gwapo-db:currency_lang to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: currency
BEGIN;

CREATE TABLE gwapese.currency_description (
  LIKE gwapese.copy_source,
  currency_id integer NOT NULL,
  CONSTRAINT currency_description_pk PRIMARY KEY (app_name, lang_tag, original,
    currency_id),
  CONSTRAINT currency_description_u UNIQUE (app_name, lang_tag, currency_id),
  CONSTRAINT currency_identifies_description_fk FOREIGN KEY (currency_id)
    REFERENCES gwapese.currency (currency_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT copy_source_identifies_currency_description_fk FOREIGN KEY
    (app_name, lang_tag, original) REFERENCES gwapese.copy_source (app_name,
    lang_tag, original) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.currency_description_history (
  LIKE gwapese.currency_description
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'currency_description', 'currency_description_history');

CREATE TABLE gwapese.currency_description_context (
  LIKE gwapese.copy_target,
  currency_id integer NOT NULL,
  CONSTRAINT currency_description_context_pk PRIMARY KEY (app_name,
    original_lang_tag, translation_lang_tag, currency_id),
  CONSTRAINT currency_description_sources_context_fk FOREIGN KEY (app_name,
    original_lang_tag, original, currency_id) REFERENCES
    gwapese.currency_description (app_name, lang_tag, original, currency_id) ON
    DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_target_identifies_currency_description_context_fk FOREIGN KEY
    (app_name, original_lang_tag, original, translation_lang_tag, translation)
    REFERENCES gwapese.copy_target (app_name, original_lang_tag, original,
    translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.currency_description_context_history (
  LIKE gwapese.currency_description_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'currency_description_context', 'currency_description_context_history');

CREATE TABLE gwapese.currency_name (
  LIKE gwapese.copy_source,
  currency_id integer NOT NULL,
  CONSTRAINT currency_name_pk PRIMARY KEY (app_name, lang_tag, original, currency_id),
  CONSTRAINT currency_name_u UNIQUE (app_name, lang_tag, currency_id),
  CONSTRAINT currency_identifies_name_fk FOREIGN KEY (currency_id) REFERENCES
    gwapese.currency (currency_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT copy_source_identifies_currency_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.copy_source (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.currency_name_history (
  LIKE gwapese.currency_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'currency_name', 'currency_name_history');

CREATE TABLE gwapese.currency_name_context (
  LIKE gwapese.copy_target,
  currency_id integer NOT NULL,
  CONSTRAINT currency_name_context_pk PRIMARY KEY (app_name, original_lang_tag,
    translation_lang_tag, currency_id),
  CONSTRAINT currency_name_sources_context_fk FOREIGN KEY (app_name,
    original_lang_tag, original, currency_id) REFERENCES gwapese.currency_name
    (app_name, lang_tag, original, currency_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT copy_target_identifies_currency_name_context_fk FOREIGN KEY
    (app_name, original_lang_tag, original, translation_lang_tag, translation)
    REFERENCES gwapese.copy_target (app_name, original_lang_tag, original,
    translation_lang_tag, translation) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.currency_name_context_history (
  LIKE gwapese.currency_name_context
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'currency_name_context', 'currency_name_context_history');

COMMIT;
