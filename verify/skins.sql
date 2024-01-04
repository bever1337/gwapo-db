-- Verify gawpo-db:skins on pg
BEGIN;

SELECT
  icon,
  rarity,
  skin_id,
  skin_type,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin
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
  gwapese.historical_skin
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
  gwapese.skin_description
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
  gwapese.historical_skin_description
WHERE
  FALSE;

SELECT
  flag,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_flag
WHERE
  FALSE;

SELECT
  flag,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_skin_flag
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
  gwapese.skin_name
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
  gwapese.historical_skin_name
WHERE
  FALSE;

SELECT
  restriction,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_restriction
WHERE
  FALSE;

SELECT
  restriction,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_skin_restriction
WHERE
  FALSE;

SELECT
  skin_id,
  slot,
  sysrange_lower,
  sysrange_upper,
  weight_class
FROM
  gwapese.armor_skin
WHERE
  FALSE;

SELECT
  skin_id,
  slot,
  sysrange_lower,
  sysrange_upper,
  weight_class
FROM
  gwapese.historical_armor_skin
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
  gwapese.armor_skin_dye_slot
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
  gwapese.historical_armor_skin_dye_slot
WHERE
  FALSE;

SELECT
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.back_skin
WHERE
  FALSE;

SELECT
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_back_skin
WHERE
  FALSE;

SELECT
  skin_id,
  tool,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.gathering_skin
WHERE
  FALSE;

SELECT
  skin_id,
  tool,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_gathering_skin
WHERE
  FALSE;

SELECT
  damage_type,
  skin_id,
  sysrange_lower,
  sysrange_upper,
  weapon_type
FROM
  gwapese.weapon_skin
WHERE
  FALSE;

SELECT
  damage_type,
  skin_id,
  sysrange_lower,
  sysrange_upper,
  weapon_type
FROM
  gwapese.historical_weapon_skin
WHERE
  FALSE;

ROLLBACK;
