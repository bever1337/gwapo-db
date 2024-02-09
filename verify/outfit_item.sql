-- Verify gwapo-db:outfit_item on pg
BEGIN;

SELECT
  item_id,
  outfit_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.outfit_item
WHERE
  FALSE;

SELECT
  item_id,
  outfit_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.outfit_item_history
WHERE
  FALSE;

ROLLBACK;
