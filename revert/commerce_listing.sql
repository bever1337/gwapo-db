-- Revert gwapo-db:commerce_listing from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'commerce_listing_buy');

DROP TABLE gwapese.commerce_listing_buy_history;

DROP TABLE gwapese.commerce_listing_buy;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'commerce_listing_sell');

DROP TABLE gwapese.commerce_listing_sell_history;

DROP TABLE gwapese.commerce_listing_sell;

COMMIT;
