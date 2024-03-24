-- Revert gwapo-db:novelty from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'novelty');

DROP TABLE gwapese.novelty_history;

DROP TABLE gwapese.novelty;

COMMIT;
