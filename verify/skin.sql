-- Verify gawpo-db:skins on pg
BEGIN;

SELECT
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin
WHERE
  FALSE;

SELECT
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_skin
WHERE
  FALSE;

SELECT
  skin_id,
  skin_type
FROM
  gwapese.skin_type
WHERE
  FALSE;

SELECT
  skin_id,
  skin_type
FROM
  gwapese.historical_skin_type
WHERE
  FALSE;

ROLLBACK;
