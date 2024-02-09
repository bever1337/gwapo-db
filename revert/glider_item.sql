-- Revert gwapo-db:glider_item from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'glider_item');

DROP TABLE gwapese.glider_item_history;

DROP TABLE gwapese.glider_item;

COMMIT;
