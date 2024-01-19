-- Verify gawpo-db:skin_gathering on pg
BEGIN;

SELECT
  skin_id,
  skin_type,
  sysrange_lower,
  sysrange_upper,
  tool
FROM
  gwapese.skin_gathering
WHERE
  FALSE;

SELECT
  skin_id,
  skin_type,
  sysrange_lower,
  sysrange_upper,
  tool
FROM
  gwapese.skin_gathering_history
WHERE
  FALSE;

ROLLBACK;
