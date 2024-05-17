-- Revert gwapo-db:currency from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'currency_currency_category');

DROP TABLE gwapese.currency_currency_category_history;

DROP TABLE gwapese.currency_currency_category;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'currency_category');

DROP TABLE gwapese.currency_category_history;

DROP TABLE gwapese.currency_category;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'currency');

DROP TABLE gwapese.currency_history;

DROP TABLE gwapese.currency;

COMMIT;
