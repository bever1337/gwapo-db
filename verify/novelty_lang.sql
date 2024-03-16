-- Verify gwapo-db:novelty_lang on pg
BEGIN;

SELECT
  app_name,
  lang_tag,
  novelty_id,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.novelty_description
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  novelty_id,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.novelty_description_history
WHERE
  FALSE;

SELECT
  app_name,
  novelty_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.novelty_description_context
WHERE
  FALSE;

SELECT
  app_name,
  novelty_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.novelty_description_context_history
WHERE
  FALSE;

SELECT
  app_name,
  novelty_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.novelty_name
WHERE
  FALSE;

SELECT
  app_name,
  novelty_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.novelty_name_history
WHERE
  FALSE;

SELECT
  app_name,
  novelty_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.novelty_name_context
WHERE
  FALSE;

SELECT
  app_name,
  novelty_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.novelty_name_context_history
WHERE
  FALSE;

ROLLBACK;
