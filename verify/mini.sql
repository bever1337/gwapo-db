-- Verify gawpo-db:mini on pg
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

SELECT
  app_name,
  lang_tag,
  mini_id,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mini_name
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  mini_id,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mini_name_history
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  mini_id,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mini_unlock
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  mini_id,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mini_unlock_history
WHERE
  FALSE;

ROLLBACK;
