-- Deploy gwapo-db:currency to pg
-- requires: schema
-- requires: history
BEGIN;

CREATE TABLE gwapese.currency (
  currency_id integer NOT NULL,
  deprecated boolean NOT NULL,
  icon text NOT NULL,
  presentation_order integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT currency_pk PRIMARY KEY (currency_id),
  CONSTRAINT currency_presentation_u UNIQUE (presentation_order)
);

CREATE TABLE gwapese.currency_history (
  LIKE gwapese.currency
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'currency', 'currency_history');

CREATE TABLE gwapese.currency_category (
  category_id integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT currency_category_pk PRIMARY KEY (category_id)
);

CREATE TABLE gwapese.currency_category_history (
  LIKE gwapese.currency_category
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'currency_category', 'currency_category_history');

CREATE TABLE gwapese.currency_currency_category (
  category_id integer NOT NULL,
  currency_id integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT currency_currency_category_pk PRIMARY KEY (category_id, currency_id),
  CONSTRAINT currency_category_identifies_currency_currency_category_fk FOREIGN
    KEY (category_id) REFERENCES gwapese.currency_category (category_id) ON
    DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT currency_identifies_currency_currency_category_fk FOREIGN KEY
    (currency_id) REFERENCES gwapese.currency (currency_id) ON DELETE CASCADE
    ON UPDATE CASCADE
);

CREATE TABLE gwapese.currency_currency_category_history (
  LIKE gwapese.currency_currency_category
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'currency_currency_category', 'currency_currency_category_history');

COMMIT;
