-- Revert gawpo-db:currencies from pg
BEGIN;

DROP TABLE gwapese.historical_currency_name;

DROP TABLE gwapese.currency_category;

DROP TABLE gwapese.currency_description;

DROP TABLE gwapese.historical_currency_description;

DROP TABLE gwapese.currency_name;

DROP TABLE gwapese.historical_currency_category;

DROP TABLE gwapese.currency;

DROP TABLE gwapese.historical_currency;

COMMIT;
