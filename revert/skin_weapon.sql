-- Revert gawpo-db:skin__weapon from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_weapon');

DROP TABLE gwapese.skin_weapon_history;

DROP TABLE gwapese.skin_weapon;

COMMIT;
