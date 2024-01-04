-- Verify gawpo-db:skin_armor_armor on pg
BEGIN;

SELECT
  icon,
  rarity,
  skin_id,
  skin_type,
  slot,
  sysrange_lower,
  sysrange_upper,
  weight_class
FROM
  gwapese.skin_armor
WHERE
  FALSE;

SELECT
  icon,
  rarity,
  skin_id,
  skin_type,
  slot,
  sysrange_lower,
  sysrange_upper,
  weight_class
FROM
  gwapese.historical_skin_armor
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
  gwapese.skin_armor_description
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
  gwapese.historical_skin_armor_description
WHERE
  FALSE;

SELECT
  color_id,
  material,
  skin_id,
  slot_index,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_armor_dye_slot
WHERE
  FALSE;

SELECT
  color_id,
  material,
  skin_id,
  slot_index,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_skin_armor_dye_slot
WHERE
  FALSE;

SELECT
  flag,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_armor_flag
WHERE
  FALSE;

SELECT
  flag,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_skin_armor_flag
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
  gwapese.skin_armor_name
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
  gwapese.historical_skin_armor_name
WHERE
  FALSE;

SELECT
  restriction,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_armor_restriction
WHERE
  FALSE;

SELECT
  restriction,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_skin_armor_restriction
WHERE
  FALSE;

ROLLBACK;
