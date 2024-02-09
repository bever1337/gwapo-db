-- Deploy gwapo-db:currency to pg
-- requires: schema
-- requires: history
-- requires: lang
BEGIN;

CREATE TABLE gwapese.currency (
  currency_id integer NOT NULL,
  deprecated boolean NOT NULL,
  icon text NOT NULL,
  presentation_order integer NOT NULL,
  CONSTRAINT currency_pk PRIMARY KEY (currency_id)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'currency');

CREATE TABLE gwapese.currency_history (
  LIKE gwapese.currency
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'currency', 'currency_history');

CREATE TABLE gwapese.currency_category (
  category integer NOT NULL,
  currency_id integer NOT NULL,
  CONSTRAINT currency_category_pk PRIMARY KEY (currency_id, category),
  CONSTRAINT currency_identifies_currency_category_fk FOREIGN KEY (currency_id)
    REFERENCES gwapese.currency (currency_id) ON DELETE CASCADE ON UPDATE
    CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'currency_category');

CREATE TABLE gwapese.currency_category_history (
  LIKE gwapese.currency_category
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'currency_category', 'currency_category_history');

CREATE TABLE gwapese.currency_description (
  app_name text NOT NULL,
  currency_id integer NOT NULL,
  lang_tag text NOT NULL,
  original text NOT NULL,
  CONSTRAINT currency_description_pk PRIMARY KEY (app_name, lang_tag, currency_id),
  CONSTRAINT currency_identifies_currency_description_fk FOREIGN KEY
    (currency_id) REFERENCES gwapese.currency (currency_id) ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT operating_copy_precedes_currency_description_fk FOREIGN KEY
    (app_name, lang_tag, original) REFERENCES gwapese.operating_copy (app_name,
    lang_tag, original) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'currency_description');

CREATE TABLE gwapese.currency_description_history (
  LIKE gwapese.currency_description
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'currency_description', 'currency_description_history');

CREATE TABLE gwapese.currency_name (
  app_name text NOT NULL,
  currency_id integer NOT NULL,
  lang_tag text NOT NULL,
  original text NOT NULL,
  CONSTRAINT currency_name_pk PRIMARY KEY (app_name, lang_tag, currency_id),
  CONSTRAINT currency_identifies_currency_name_fk FOREIGN KEY (currency_id)
    REFERENCES gwapese.currency (currency_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT operating_copy_precedes_currency_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.operating_copy (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'currency_name');

CREATE TABLE gwapese.currency_name_history (
  LIKE gwapese.currency_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'currency_name', 'currency_name_history');

COMMIT;
