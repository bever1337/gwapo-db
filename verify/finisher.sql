-- Verify gwapo-db:finisher on pg
BEGIN;

SELECT
  finisher_id,
  icon,
  presentation_order,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.finisher
WHERE
  FALSE;

SELECT
  finisher_id,
  icon,
  presentation_order,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.finisher_history
WHERE
  FALSE;

ROLLBACK;
