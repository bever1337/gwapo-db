-- Revert gawpo-db:currencies from pg
BEGIN;

DROP TABLE gwapese.named_currencies;

DROP TABLE gwapese.described_currencies;

DROP PROCEDURE gwapese.upsert_currency;

DROP PROCEDURE gwapese.upsert_currency_description;

DROP PROCEDURE gwapese.upsert_currency_name;

DROP FUNCTION gwapese.select_currencies;

DROP TABLE gwapese.currencies;

COMMIT;
