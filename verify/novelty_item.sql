-- Verify gwapo-db:novelty_item on pg
BEGIN;

SELECT
  item_id,
  novelty_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.novelty_item
WHERE
  FALSE;

SELECT
  item_id,
  novelty_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.novelty_item_history
WHERE
  FALSE;

ROLLBACK;
