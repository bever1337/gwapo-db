-- Revert gwapo-db:outfit from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'outfit');

DROP TABLE gwapese.outfit_history;

DROP TABLE gwapese.outfit;

COMMIT;
