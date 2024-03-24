-- Verify gwapo-db:currency_lang on pg
BEGIN;

SELECT
  app_name,
  currency_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.currency_description
WHERE
  FALSE;

SELECT
  app_name,
  currency_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.currency_description_history
WHERE
  FALSE;

SELECT
  app_name,
  currency_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.currency_description_context
WHERE
  FALSE;

SELECT
  app_name,
  currency_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.currency_description_context_history
WHERE
  FALSE;

SELECT
  app_name,
  currency_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.currency_name
WHERE
  FALSE;

SELECT
  app_name,
  currency_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.currency_name_history
WHERE
  FALSE;

SELECT
  app_name,
  currency_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.currency_name_context
WHERE
  FALSE;

SELECT
  app_name,
  currency_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.currency_name_context_history
WHERE
  FALSE;

ROLLBACK;
