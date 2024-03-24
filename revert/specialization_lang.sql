-- Revert gwapo-db:specialization_lang from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'specialization_name_context');

DROP TABLE gwapese.specialization_name_context_history;

DROP TABLE gwapese.specialization_name_context;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'specialization_name');

DROP TABLE gwapese.specialization_name_history;

DROP TABLE gwapese.specialization_name;

COMMIT;
