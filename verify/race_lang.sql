-- Verify gwapo-db:race_lang on pg
BEGIN;

SELECT
  app_name,
  lang_tag,
  original,
  race_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.race_name
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  original,
  race_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.race_name_history
WHERE
  FALSE;

SELECT
  app_name,
  original_lang_tag,
  original,
  race_id,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.race_name_context
WHERE
  FALSE;

SELECT
  app_name,
  original_lang_tag,
  original,
  race_id,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.race_name_context_history
WHERE
  FALSE;

ROLLBACK;
