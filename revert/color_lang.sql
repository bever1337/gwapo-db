-- Revert gwapo-db:color_lang from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'color_name_context');

DROP TABLE gwapese.color_name_context_history;

DROP TABLE gwapese.color_name_context;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'color_name');

DROP TABLE gwapese.color_name_history;

DROP TABLE gwapese.color_name;

COMMIT;
