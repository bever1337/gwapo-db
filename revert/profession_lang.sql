-- Revert gwapo-db:profession_lang from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'profession_name_context');

DROP TABLE gwapese.profession_name_context_history;

DROP TABLE gwapese.profession_name_context;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'profession_name');

DROP TABLE gwapese.profession_name_history;

DROP TABLE gwapese.profession_name;

COMMIT;
