-- Verify gawpo-db:skin_back_back on pg
BEGIN;

SELECT
  icon,
  rarity,
  skin_id,
  skin_type,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_back
WHERE
  FALSE;

SELECT
  icon,
  rarity,
  skin_id,
  skin_type,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_skin_back
WHERE
  FALSE;

SELECT
  app_name,
  original,
  lang_tag,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_back_description
WHERE
  FALSE;

SELECT
  app_name,
  original,
  lang_tag,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_skin_back_description
WHERE
  FALSE;

SELECT
  flag,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_back_flag
WHERE
  FALSE;

SELECT
  flag,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_skin_back_flag
WHERE
  FALSE;

SELECT
  app_name,
  original,
  lang_tag,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_back_name
WHERE
  FALSE;

SELECT
  app_name,
  original,
  lang_tag,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_skin_back_name
WHERE
  FALSE;

SELECT
  restriction,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_back_restriction
WHERE
  FALSE;

SELECT
  restriction,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_skin_back_restriction
WHERE
  FALSE;

ROLLBACK;
