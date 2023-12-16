-- Verify gawpo-db:weapons on pg
BEGIN;

SELECT
  damage_type
FROM
  gwapese.damage_types
WHERE
  FALSE;

SELECT
  weapon_type
FROM
  gwapese.weapon_types
WHERE
  FALSE;

ROLLBACK;
