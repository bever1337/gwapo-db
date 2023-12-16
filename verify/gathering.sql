-- Verify gawpo-db:gathering on pg
BEGIN;

SELECT
  tool
FROM
  gwapese.gathering_tools
WHERE
  FALSE;

ROLLBACK;
