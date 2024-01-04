-- Revert gawpo-db:lang from pg
BEGIN;

DROP PROCEDURE gwapese.delete_operating_copy;

DROP PROCEDURE gwapese.delete_translated_copy;

DROP PROCEDURE gwapese.upsert_operating_copy;

DROP PROCEDURE gwapese.upsert_translated_copy;

DROP TABLE gwapese.historical_translated_copy;

DROP TABLE gwapese.translated_copy;

DROP TABLE gwapese.historical_operating_copy;

DROP TABLE gwapese.operating_copy;

DROP TABLE gwapese.historical_operating_lang;

DROP TABLE gwapese.operating_lang;

DROP TABLE gwapese.historical_app;

DROP TABLE gwapese.app;

DROP TABLE gwapese.historical_lang;

DROP TABLE gwapese.lang;

COMMIT;
