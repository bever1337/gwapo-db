-- Revert gwapo-db:skiff_lang from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skiff_name_context');

DROP TABLE gwapese.skiff_name_context_history;

DROP TABLE gwapese.skiff_name_context;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skiff_name');

DROP TABLE gwapese.skiff_name_history;

DROP TABLE gwapese.skiff_name;

COMMIT;
