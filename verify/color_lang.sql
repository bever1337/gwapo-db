-- Verify gwapo-db:color_lang on pg
BEGIN;

SELECT
  app_name,
  color_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.color_name
WHERE
  FALSE;

SELECT
  app_name,
  color_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.color_name_history
WHERE
  FALSE;

SELECT
  app_name,
  color_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.color_name_context
WHERE
  FALSE;

SELECT
  app_name,
  color_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.color_name_context_history
WHERE
  FALSE;

ROLLBACK;
