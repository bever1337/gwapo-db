-- Verify gwapo-db:mini on pg
BEGIN;

SELECT
  icon,
  mini_id,
  presentation_order,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mini
WHERE
  FALSE;

SELECT
  icon,
  mini_id,
  presentation_order,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mini_history
WHERE
  FALSE;

ROLLBACK;
