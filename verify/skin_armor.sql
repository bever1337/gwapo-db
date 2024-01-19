-- Verify gawpo-db:skin_armor_armor on pg
BEGIN;

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

ROLLBACK;
