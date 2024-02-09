-- Revert gwapo-db:currency from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'currency_category');

DROP TABLE gwapese.currency_category_history;

DROP TABLE gwapese.currency_category;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'currency_description');

DROP TABLE gwapese.currency_description_history;

DROP TABLE gwapese.currency_description;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'currency_name');

DROP TABLE gwapese.currency_name_history;

DROP TABLE gwapese.currency_name;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'currency');

DROP TABLE gwapese.currency_history;

DROP TABLE gwapese.currency;

COMMIT;
