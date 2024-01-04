-- Verify gawpo-db:skin_gathering on pg
BEGIN;

SELECT
  icon,
  rarity,
  skin_id,
  skin_type,
  tool,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_gathering
WHERE
  FALSE;

SELECT
  icon,
  rarity,
  skin_id,
  skin_type,
  tool,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_skin_gathering
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
  gwapese.skin_gathering_description
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
  gwapese.historical_skin_gathering_description
WHERE
  FALSE;

SELECT
  flag,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_gathering_flag
WHERE
  FALSE;

SELECT
  flag,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_skin_gathering_flag
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
  gwapese.skin_gathering_name
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
  gwapese.historical_skin_gathering_name
WHERE
  FALSE;

SELECT
  restriction,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_gathering_restriction
WHERE
  FALSE;

SELECT
  restriction,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_skin_gathering_restriction
WHERE
  FALSE;

ROLLBACK;
