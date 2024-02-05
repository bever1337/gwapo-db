-- Verify gawpo-db:finisher_item on pg
BEGIN;

SELECT
  finisher_id,
  item_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.finisher_item
WHERE
  FALSE;

SELECT
  finisher_id,
  item_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.finisher_item_history
WHERE
  FALSE;

ROLLBACK;
