-- Revert gawpo-db:currency from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'currency_category',
  'historical_currency_category');

DROP TABLE gwapese.historical_currency_category;

DROP TABLE gwapese.currency_category;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'currency_description',
  'historical_currency_description');

DROP TABLE gwapese.historical_currency_description;

DROP TABLE gwapese.currency_description;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'currency_name',
  'historical_currency_name');

DROP TABLE gwapese.historical_currency_name;

DROP TABLE gwapese.currency_name;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'currency',
  'historical_currency');

DROP TABLE gwapese.historical_currency;

DROP TABLE gwapese.currency;

COMMIT;
