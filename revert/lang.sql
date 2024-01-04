-- Revert gawpo-db:lang from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'translated_copy',
  'historical_translated_copy');

DROP TABLE gwapese.historical_translated_copy;

DROP TABLE gwapese.translated_copy;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'operating_copy',
  'historical_operating_copy');

DROP TABLE gwapese.historical_operating_copy;

DROP TABLE gwapese.operating_copy;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'operating_lang',
  'historical_operating_lang');

DROP TABLE gwapese.historical_operating_lang;

DROP TABLE gwapese.operating_lang;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'app',
  'historical_app');

DROP TABLE gwapese.historical_app;

DROP TABLE gwapese.app;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'lang',
  'historical_lang');

DROP TABLE gwapese.historical_lang;

DROP TABLE gwapese.lang;

COMMIT;
