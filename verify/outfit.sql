-- Verify gwapo-db:outfit on pg
BEGIN;

SELECT
  icon,
  outfit_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.outfit
WHERE
  FALSE;

SELECT
  icon,
  outfit_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.outfit_history
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  original,
  outfit_id
FROM
  gwapese.outfit_name
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  original,
  outfit_id
FROM
  gwapese.outfit_name_history
WHERE
  FALSE;

ROLLBACK;
