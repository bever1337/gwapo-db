-- Verify gawpo-db:race on pg
BEGIN;

SELECT
  race_name,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.race
WHERE
  FALSE;

SELECT
  race_name,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_race
WHERE
  FALSE;

ROLLBACK;
