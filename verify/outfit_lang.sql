-- Verify gwapo-db:outfit_lang on pg
BEGIN;

SELECT
  app_name,
  lang_tag,
  original,
  outfit_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.outfit_name
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  original,
  outfit_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.outfit_name_history
WHERE
  FALSE;

SELECT
  app_name,
  original_lang_tag,
  original,
  outfit_id,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.outfit_name_context
WHERE
  FALSE;

SELECT
  app_name,
  original_lang_tag,
  original,
  outfit_id,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.outfit_name_context_history
WHERE
  FALSE;

ROLLBACK;
