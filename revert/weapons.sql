-- Revert gawpo-db:weapons from pg
BEGIN;

DROP TABLE gwapese.damage_types;

DROP TABLE gwapese.weapon_types;

COMMIT;
