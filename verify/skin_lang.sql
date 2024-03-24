-- Verify gwapo-db:skin_lang on pg
BEGIN;

SELECT
  app_name,
  lang_tag,
  original,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_description
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  original,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_description_history
WHERE
  FALSE;

SELECT
  app_name,
  original_lang_tag,
  original,
  skin_id,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.skin_description_context
WHERE
  FALSE;

SELECT
  app_name,
  original_lang_tag,
  original,
  skin_id,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.skin_description_context_history
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  original,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_name
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  original,
  skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skin_name_history
WHERE
  FALSE;

SELECT
  app_name,
  original_lang_tag,
  original,
  skin_id,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.skin_name_context
WHERE
  FALSE;

SELECT
  app_name,
  original_lang_tag,
  original,
  skin_id,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.skin_name_context_history
WHERE
  FALSE;

ROLLBACK;
