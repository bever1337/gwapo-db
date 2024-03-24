-- Verify gwapo-db:mini_lang on pg
BEGIN;

SELECT
  app_name,
  mini_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mini_name
WHERE
  FALSE;

SELECT
  app_name,
  mini_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mini_name_history
WHERE
  FALSE;

SELECT
  app_name,
  mini_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.mini_name_context
WHERE
  FALSE;

SELECT
  app_name,
  mini_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.mini_name_context_history
WHERE
  FALSE;

SELECT
  app_name,
  mini_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mini_unlock
WHERE
  FALSE;

SELECT
  app_name,
  mini_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mini_unlock_history
WHERE
  FALSE;

SELECT
  app_name,
  mini_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.mini_unlock_context
WHERE
  FALSE;

SELECT
  app_name,
  mini_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.mini_unlock_context_history
WHERE
  FALSE;

ROLLBACK;
