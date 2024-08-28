-- Deploy gwapo-db:commerce_listing to pg
-- requires: schema
-- requires: history
-- requires: item
BEGIN;

CREATE TABLE gwapese.commerce_listing_buy (
  item_id integer NOT NULL,
  listings integer NOT NULL,
  quantity integer NOT NULL,
  recorded timestamp(3) NOT NULL,
  unit_price integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT commerce_listing_buy_pk PRIMARY KEY (item_id, unit_price, recorded),
  CONSTRAINT item_identifies_commerce_listing_buy_fk FOREIGN KEY (item_id)
    REFERENCES gwapese.item (item_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.commerce_listing_buy_history (
  LIKE gwapese.commerce_listing_buy
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'commerce_listing_buy', 'commerce_listing_buy_history');

CREATE TABLE gwapese.commerce_listing_sell (
  item_id integer NOT NULL,
  listings integer NOT NULL,
  quantity integer NOT NULL,
  recorded timestamp(3) NOT NULL,
  unit_price integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT commerce_listing_sell_pk PRIMARY KEY (item_id, unit_price, recorded),
  CONSTRAINT item_identifies_commerce_listing_sell_fk FOREIGN KEY (item_id)
    REFERENCES gwapese.item (item_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.commerce_listing_sell_history (
  LIKE gwapese.commerce_listing_sell
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'commerce_listing_sell', 'commerce_listing_sell_history');

COMMIT;
