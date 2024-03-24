-- Verify gwapo-db:item_lang on pg
BEGIN;

SELECT
  app_name,
  item_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.item_description
WHERE
  FALSE;

SELECT
  app_name,
  item_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.item_description_history
WHERE
  FALSE;

SELECT
  app_name,
  item_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.item_description_context
WHERE
  FALSE;

SELECT
  app_name,
  item_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.item_description_context_history
WHERE
  FALSE;

SELECT
  app_name,
  item_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.item_name
WHERE
  FALSE;

SELECT
  app_name,
  item_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.item_name_history
WHERE
  FALSE;

SELECT
  app_name,
  item_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.item_name_context
WHERE
  FALSE;

SELECT
  app_name,
  item_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.item_name_context_history
WHERE
  FALSE;

ROLLBACK;
