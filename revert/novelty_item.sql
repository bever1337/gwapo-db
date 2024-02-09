-- Revert gwapo-db:novelty_item from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'novelty_item');

DROP TABLE gwapese.novelty_item_history;

DROP TABLE gwapese.novelty_item;

COMMIT;
