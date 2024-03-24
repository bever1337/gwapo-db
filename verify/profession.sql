-- Verify gwapo-db:profession on pg
BEGIN;

SELECT
  icon,
  profession_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.profession
WHERE
  FALSE;

SELECT
  icon,
  profession_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.profession_history
WHERE
  FALSE;

ROLLBACK;
