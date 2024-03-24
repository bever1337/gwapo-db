-- Revert gwapo-db:jade_bot from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'jade_bot');

DROP TABLE gwapese.jade_bot_history;

DROP TABLE gwapese.jade_bot;

COMMIT;
