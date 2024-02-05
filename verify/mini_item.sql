-- Verify gawpo-db:mini_item on pg
BEGIN;

SELECT
  item_id,
  mini_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mini_item
WHERE
  FALSE;

SELECT
  item_id,
  mini_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mini_item_history
WHERE
  FALSE;

ROLLBACK;
