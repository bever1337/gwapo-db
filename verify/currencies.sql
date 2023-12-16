-- Verify gawpo-db:currencies on pg
BEGIN;

SELECT
  id,
  categories,
  deprecated,
  icon,
  presentation_order
FROM
  gwapese.currencies
WHERE
  FALSE;

SELECT
  id,
  currency_description,
  language_tag
FROM
  gwapese.described_currencies
WHERE
  FALSE;

SELECT
  id,
  currency_name,
  language_tag
FROM
  gwapese.named_currencies
WHERE
  FALSE;

SELECT
  HAS_FUNCTION_PRIVILEGE('gwapese.select_currencies(text)', 'execute');

SELECT
  HAS_FUNCTION_PRIVILEGE('gwapese.upsert_currency(SMALLINT, SMALLINT[], BOOLEAN, TEXT, SMALLINT)', 'execute');

SELECT
  HAS_FUNCTION_PRIVILEGE('gwapese.upsert_currency_description(SMALLINT, TEXT, text)', 'execute');

SELECT
  HAS_FUNCTION_PRIVILEGE('gwapese.upsert_currency_name(SMALLINT, TEXT, text)', 'execute');

ROLLBACK;
