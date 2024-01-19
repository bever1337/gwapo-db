-- Revert gawpo-db:skin__armor from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_armor_dye_slot');

DROP TABLE gwapese.skin_armor_dye_slot_history;

DROP TABLE gwapese.skin_armor_dye_slot;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_armor');

DROP TABLE gwapese.skin_armor_history;

DROP TABLE gwapese.skin_armor;

COMMIT;
