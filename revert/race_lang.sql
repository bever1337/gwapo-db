-- Revert gwapo-db:race_lang from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'race_name_context');

DROP TABLE gwapese.race_name_context_history;

DROP TABLE gwapese.race_name_context;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'race_name');

DROP TABLE gwapese.race_name_history;

DROP TABLE gwapese.race_name;

COMMIT;
