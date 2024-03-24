-- Verify gwapo-db:profession_lang on pg
BEGIN;

SELECT
  app_name,
  lang_tag,
  original,
  profession_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.profession_name
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  original,
  profession_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.profession_name_history
WHERE
  FALSE;

SELECT
  app_name,
  original_lang_tag,
  original,
  profession_id,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.profession_name_context
WHERE
  FALSE;

SELECT
  app_name,
  original_lang_tag,
  original,
  profession_id,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.profession_name_context_history
WHERE
  FALSE;

ROLLBACK;
