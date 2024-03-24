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
  CONSTRAINT currency_pk PRIMARY KEY (currency_id)
);

CREATE TABLE gwapese.currency_history (
  LIKE gwapese.currency
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'currency', 'currency_history');

CREATE TABLE gwapese.currency_category (
  category integer NOT NULL,
  currency_id integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT currency_category_pk PRIMARY KEY (currency_id, category),
  CONSTRAINT currency_identifies_category_fk FOREIGN KEY (currency_id)
    REFERENCES gwapese.currency (currency_id) ON DELETE CASCADE ON UPDATE
    CASCADE
);

CREATE TABLE gwapese.currency_category_history (
  LIKE gwapese.currency_category
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'currency_category', 'currency_category_history');

COMMIT;
