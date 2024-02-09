-- Verify gwapo-db:lang on pg
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
  gwapese.lang_history
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
  gwapese.app_history
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
  gwapese.operating_lang_history
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
  gwapese.operating_copy_history
WHERE
  FALSE;

SELECT
  app_name,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.translated_copy
WHERE
  FALSE;

SELECT
  app_name,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.translated_copy_history
WHERE
  FALSE;

ROLLBACK;
