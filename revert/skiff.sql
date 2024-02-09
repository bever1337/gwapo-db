-- Revert gwapo-db:skiff from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skiff_dye_slot');

DROP TABLE gwapese.skiff_dye_slot_history;

DROP TABLE gwapese.skiff_dye_slot;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skiff_name');

DROP TABLE gwapese.skiff_name_history;

DROP TABLE gwapese.skiff_name;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skiff');

DROP TABLE gwapese.skiff_history;

DROP TABLE gwapese.skiff;

COMMIT;
