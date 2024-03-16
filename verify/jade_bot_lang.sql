-- Verify gwapo-db:jade_bot_lang on pg
BEGIN;

SELECT
  app_name,
  jade_bot_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.jade_bot_description
WHERE
  FALSE;

SELECT
  app_name,
  jade_bot_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.jade_bot_description_history
WHERE
  FALSE;

SELECT
  app_name,
  jade_bot_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.jade_bot_description_context
WHERE
  FALSE;

SELECT
  app_name,
  jade_bot_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.jade_bot_description_context_history
WHERE
  FALSE;

SELECT
  app_name,
  jade_bot_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.jade_bot_name
WHERE
  FALSE;

SELECT
  app_name,
  jade_bot_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.jade_bot_name_history
WHERE
  FALSE;

SELECT
  app_name,
  jade_bot_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.jade_bot_name_context
WHERE
  FALSE;

SELECT
  app_name,
  jade_bot_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.jade_bot_name_context_history
WHERE
  FALSE;

ROLLBACK;
