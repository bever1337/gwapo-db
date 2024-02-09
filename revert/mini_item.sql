-- Revert gwapo-db:mini_item from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'mini_item');

DROP TABLE gwapese.mini_item_history;

DROP TABLE gwapese.mini_item;

COMMIT;
