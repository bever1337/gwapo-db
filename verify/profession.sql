-- Verify gawpo-db:profession on pg
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

SELECT
  app_name,
  lang_tag,
  original,
  profession_id
FROM
  gwapese.profession_name
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  original,
  profession_id
FROM
  gwapese.profession_name_history
WHERE
  FALSE;

ROLLBACK;
