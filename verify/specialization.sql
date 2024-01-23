-- Verify gawpo-db:specialization on pg
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

SELECT
  app_name,
  lang_tag,
  original,
  specialization_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.specialization_name
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  original,
  specialization_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.specialization_name_history
WHERE
  FALSE;

ROLLBACK;
