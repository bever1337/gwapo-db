-- Revert gwapo-db:currency_lang from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'currency_description_context');

DROP TABLE gwapese.currency_description_context_history;

DROP TABLE gwapese.currency_description_context;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'currency_description');

DROP TABLE gwapese.currency_description_history;

DROP TABLE gwapese.currency_description;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'currency_name_context');

DROP TABLE gwapese.currency_name_context_history;

DROP TABLE gwapese.currency_name_context;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'currency_name');

DROP TABLE gwapese.currency_name_history;

DROP TABLE gwapese.currency_name;

COMMIT;
