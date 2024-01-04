-- Verify gawpo-db:skin_weapon_weapon on pg
BEGIN;

SELECT
  damage_type,
  icon,
  rarity,
  skin_id,
  skin_type,
  sysrange_lower,
  sysrange_upper,
  weapon_type
FROM
  gwapese.skin_weapon
WHERE
  FALSE;

SELECT
  damage_type,
  icon,
  rarity,
  skin_id,
  skin_type,
  sysrange_lower,
  sysrange_upper,
  weapon_type
FROM
  gwapese.historical_skin_weapon
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
  gwapese.skin_weapon_description
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
  gwapese.historical_skin_weapon_description
WHERE
  FALSE;

SELECT
  flag,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_weapon_flag
WHERE
  FALSE;

SELECT
  flag,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_skin_weapon_flag
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
  gwapese.skin_weapon_name
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
  gwapese.historical_skin_weapon_name
WHERE
  FALSE;

SELECT
  restriction,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_weapon_restriction
WHERE
  FALSE;

SELECT
  restriction,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_skin_weapon_restriction
WHERE
  FALSE;

ROLLBACK;
