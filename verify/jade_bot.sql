-- Verify gwapo-db:jade_bot on pg
BEGIN;

SELECT
  jade_bot_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.jade_bot
WHERE
  FALSE;

SELECT
  jade_bot_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.jade_bot_history
WHERE
  FALSE;

ROLLBACK;
