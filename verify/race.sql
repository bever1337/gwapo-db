-- Verify gawpo-db:race on pg
BEGIN;

SELECT
  race_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.race
WHERE
  FALSE;

SELECT
  race_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.race_history
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  original,
  race_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.race_name
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  original,
  race_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.race_name_history
WHERE
  FALSE;

ROLLBACK;
