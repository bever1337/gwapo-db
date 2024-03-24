-- Revert gwapo-db:finisher from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'finisher');

DROP TABLE gwapese.finisher_history;

DROP TABLE gwapese.finisher;

COMMIT;
