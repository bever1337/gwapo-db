-- Verify gawpo-db:skin_weapon_weapon on pg
BEGIN;

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
