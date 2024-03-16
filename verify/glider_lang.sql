-- Verify gwapo-db:glider_lang on pg
BEGIN;

SELECT
  app_name,
  glider_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.glider_description
WHERE
  FALSE;

SELECT
  app_name,
  glider_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.glider_description_history
WHERE
  FALSE;

SELECT
  app_name,
  glider_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.glider_description_context
WHERE
  FALSE;

SELECT
  app_name,
  glider_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.glider_description_context_history
WHERE
  FALSE;

SELECT
  app_name,
  glider_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.glider_name
WHERE
  FALSE;

SELECT
  app_name,
  glider_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.glider_name_history
WHERE
  FALSE;

SELECT
  app_name,
  glider_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.glider_name_context
WHERE
  FALSE;

SELECT
  app_name,
  glider_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.glider_name_context_history
WHERE
  FALSE;

ROLLBACK;
