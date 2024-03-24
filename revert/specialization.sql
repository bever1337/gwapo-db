-- Revert gwapo-db:specialization from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'specialization');

DROP TABLE gwapese.specialization_history;

DROP TABLE gwapese.specialization;

COMMIT;
