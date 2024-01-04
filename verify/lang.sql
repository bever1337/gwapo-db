-- Verify gawpo-db:lang on pg
BEGIN;

SELECT
  lang_tag,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.lang
WHERE
  FALSE;

SELECT
  lang_tag,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_lang
WHERE
  FALSE;

SELECT
  app_name,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.app
WHERE
  FALSE;

SELECT
  app_name,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_app
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.operating_lang
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_operating_lang
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.operating_copy
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_operating_copy
WHERE
  FALSE;

SELECT
  app_name,
  original_lang_tag,
  original,
  translation_lang_tag,
  translation,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.translated_copy
WHERE
  FALSE;

SELECT
  app_name,
  original_lang_tag,
  original,
  translation_lang_tag,
  translation,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_translated_copy
WHERE
  FALSE;

SELECT
  HAS_FUNCTION_PRIVILEGE('gwapese.upsert_operating_copy(text, text, text)', 'execute');

SELECT
  HAS_FUNCTION_PRIVILEGE('gwapese.delete_operating_copy(text, text, text)', 'execute');

SELECT
  HAS_FUNCTION_PRIVILEGE('gwapese.upsert_translated_copy(text, text, text, text, text)', 'execute');

SELECT
  HAS_FUNCTION_PRIVILEGE('gwapese.delete_translated_copy(text, text, text, text)', 'execute');

ROLLBACK;
