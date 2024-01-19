-- Verify gawpo-db:skin_back_back on pg
BEGIN;

SELECT
  skin_id,
  skin_type,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_back
WHERE
  FALSE;

SELECT
  skin_id,
  skin_type,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_back_history
WHERE
  FALSE;

ROLLBACK;
