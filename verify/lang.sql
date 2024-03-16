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
  document,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.copy_document
WHERE
  FALSE;

SELECT
  app_name,
  document,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.copy_document_history
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
  gwapese.copy_source
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.copy_source_history
WHERE
  FALSE;

SELECT
  app_name,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.copy_target
WHERE
  FALSE;

SELECT
  app_name,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.copy_target_history
WHERE
  FALSE;

ROLLBACK;
