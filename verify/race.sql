-- Verify gwapo-db:race on pg
BEGIN;

SELECT
  race_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.race
WHERE
  FALSE;

SELECT
  race_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.race_history
WHERE
  FALSE;

ROLLBACK;
