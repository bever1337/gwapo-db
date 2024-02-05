-- Revert gawpo-db:finisher_item from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'finisher_item');

DROP TABLE gwapese.finisher_item_history;

DROP TABLE gwapese.finisher_item;

COMMIT;
