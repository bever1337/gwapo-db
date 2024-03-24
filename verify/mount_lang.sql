-- Verify gwapo-db:mount_lang on pg
BEGIN;

SELECT
  app_name,
  lang_tag,
  mount_id,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mount_name
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  mount_id,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mount_name_history
WHERE
  FALSE;

SELECT
  app_name,
  mount_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.mount_name_context
WHERE
  FALSE;

SELECT
  app_name,
  mount_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.mount_name_context_history
WHERE
  FALSE;

ROLLBACK;
