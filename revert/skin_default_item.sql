-- Revert gwapo-db:skin_default_item from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_default_item');

DROP TABLE gwapese.skin_default_item_history;

DROP TABLE gwapese.skin_default_item;

COMMIT;
