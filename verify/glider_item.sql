-- Verify gawpo-db:glider_item on pg
BEGIN;

SELECT
  glider_id,
  item_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.glider_item
WHERE
  FALSE;

SELECT
  glider_id,
  item_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.glider_item_history
WHERE
  FALSE;

ROLLBACK;
