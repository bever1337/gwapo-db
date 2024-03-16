-- Revert gwapo-db:outfit_lang from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'outfit_name_context');

DROP TABLE gwapese.outfit_name_context_history;

DROP TABLE gwapese.outfit_name_context;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'outfit_name');

DROP TABLE gwapese.outfit_name_history;

DROP TABLE gwapese.outfit_name;

COMMIT;
