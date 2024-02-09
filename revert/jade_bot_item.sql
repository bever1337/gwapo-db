-- Revert gwapo-db:jade_bot_item from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'jade_bot_item');

DROP TABLE gwapese.jade_bot_item_history;

DROP TABLE gwapese.jade_bot_item;

COMMIT;
