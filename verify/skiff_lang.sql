-- Verify gwapo-db:skiff_lang on pg
BEGIN;

SELECT
  app_name,
  lang_tag,
  original,
  skiff_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skiff_name
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  original,
  skiff_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skiff_name_history
WHERE
  FALSE;

SELECT
  app_name,
  original_lang_tag,
  original,
  skiff_id,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.skiff_name_context
WHERE
  FALSE;

SELECT
  app_name,
  original_lang_tag,
  original,
  skiff_id,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.skiff_name_context_history
WHERE
  FALSE;

ROLLBACK;
