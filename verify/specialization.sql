-- Verify gwapo-db:specialization on pg
BEGIN;

SELECT
  background,
  elite,
  icon,
  profession_id,
  specialization_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.specialization
WHERE
  FALSE;

SELECT
  background,
  elite,
  icon,
  profession_id,
  specialization_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.specialization_history
WHERE
  FALSE;

ROLLBACK;
