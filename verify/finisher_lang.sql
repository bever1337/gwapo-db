-- Verify gwapo-db:finisher_lang on pg
BEGIN;

SELECT
  app_name,
  finisher_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.finisher_detail
WHERE
  FALSE;

SELECT
  app_name,
  finisher_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.finisher_detail_history
WHERE
  FALSE;

SELECT
  app_name,
  finisher_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.finisher_detail_context
WHERE
  FALSE;

SELECT
  app_name,
  finisher_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.finisher_detail_context_history
WHERE
  FALSE;

SELECT
  app_name,
  finisher_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.finisher_name
WHERE
  FALSE;

SELECT
  app_name,
  finisher_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.finisher_name_history
WHERE
  FALSE;

SELECT
  app_name,
  finisher_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.finisher_name_context
WHERE
  FALSE;

SELECT
  app_name,
  finisher_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.finisher_name_context_history
WHERE
  FALSE;

ROLLBACK;
