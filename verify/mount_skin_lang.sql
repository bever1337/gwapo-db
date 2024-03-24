-- Verify gwapo-db:mount_skin_lang on pg
BEGIN;

SELECT
  app_name,
  lang_tag,
  mount_skin_id,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mount_skin_name
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  mount_skin_id,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mount_skin_name_history
WHERE
  FALSE;

SELECT
  app_name,
  mount_skin_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.mount_skin_name_context
WHERE
  FALSE;

SELECT
  app_name,
  mount_skin_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.mount_skin_name_context_history
WHERE
  FALSE;

ROLLBACK;
