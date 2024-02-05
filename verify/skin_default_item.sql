-- Verify gawpo-db:skin_default_item on pg
BEGIN;

SELECT
  item_id,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_default_item
WHERE
  FALSE;

SELECT
  item_id,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_default_item_history
WHERE
  FALSE;

ROLLBACK;
