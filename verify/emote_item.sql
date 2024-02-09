-- Verify gwapo-db:emote_item on pg
BEGIN;

SELECT
  emote_id,
  item_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.emote_item
WHERE
  FALSE;

SELECT
  emote_id,
  item_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.emote_item_history
WHERE
  FALSE;

ROLLBACK;
