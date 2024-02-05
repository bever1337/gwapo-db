-- Verify gawpo-db:jade_bot_item on pg
BEGIN;

SELECT
  item_id,
  jade_bot_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.jade_bot_item
WHERE
  FALSE;

SELECT
  item_id,
  jade_bot_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.jade_bot_item_history
WHERE
  FALSE;

ROLLBACK;
