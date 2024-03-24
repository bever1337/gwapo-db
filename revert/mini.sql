-- Revert gwapo-db:mini from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'mini');

DROP TABLE gwapese.mini_history;

DROP TABLE gwapese.mini;

COMMIT;
