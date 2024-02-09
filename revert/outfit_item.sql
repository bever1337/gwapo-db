-- Revert gwapo-db:outfit_item from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'outfit_item');

DROP TABLE gwapese.outfit_item_history;

DROP TABLE gwapese.outfit_item;

COMMIT;
