-- Verify gawpo-db:races on pg
BEGIN;

SELECT
  race
FROM
  gwapese.races
WHERE
  FALSE;

SELECT
  HAS_FUNCTION_PRIVILEGE('gwapese.insert_race(text)', 'execute');

ROLLBACK;
