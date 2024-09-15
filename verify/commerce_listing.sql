-- Verify gwapo-db:commerce_listing on pg
BEGIN;

SELECT
  item_id,
  recorded,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.commerce_listing_buy
WHERE
  FALSE;

SELECT
  item_id,
  recorded,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.commerce_listing_buy_history
WHERE
  FALSE;

SELECT
  item_id,
  recorded,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.commerce_listing_sell
WHERE
  FALSE;

SELECT
  item_id,
  recorded,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.commerce_listing_sell_history
WHERE
  FALSE;

ROLLBACK;
