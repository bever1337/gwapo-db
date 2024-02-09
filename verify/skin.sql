-- Verify gwapo-db:skins on pg
BEGIN;

SELECT
  icon,
  rarity,
  skin_id,
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
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_history
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
  gwapese.skin_description_history
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
  gwapese.skin_flag_history
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
  gwapese.skin_name_history
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
  gwapese.skin_restriction_history
WHERE
  FALSE;

SELECT
  skin_id,
  skin_type,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_type
WHERE
  FALSE;

SELECT
  skin_id,
  skin_type,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_type_history
WHERE
  FALSE;

SELECT
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
  skin_id,
  skin_type,
  slot,
  sysrange_lower,
  sysrange_upper,
  weight_class
FROM
  gwapese.skin_armor_history
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
  gwapese.skin_armor_dye_slot_history
WHERE
  FALSE;

SELECT
  skin_id,
  skin_type,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_back
WHERE
  FALSE;

SELECT
  skin_id,
  skin_type,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_back_history
WHERE
  FALSE;

SELECT
  skin_id,
  skin_type,
  sysrange_lower,
  sysrange_upper,
  tool
FROM
  gwapese.skin_gathering
WHERE
  FALSE;

SELECT
  skin_id,
  skin_type,
  sysrange_lower,
  sysrange_upper,
  tool
FROM
  gwapese.skin_gathering_history
WHERE
  FALSE;

SELECT
  damage_type,
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
  skin_id,
  skin_type,
  sysrange_lower,
  sysrange_upper,
  weapon_type
FROM
  gwapese.skin_weapon_history
WHERE
  FALSE;

ROLLBACK;
