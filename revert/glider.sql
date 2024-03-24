-- Revert gwapo-db:glider from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'glider_dye_slot');

DROP TABLE gwapese.glider_dye_slot_history;

DROP TABLE gwapese.glider_dye_slot;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'glider');

DROP TABLE gwapese.glider_history;

DROP TABLE gwapese.glider;

COMMIT;
