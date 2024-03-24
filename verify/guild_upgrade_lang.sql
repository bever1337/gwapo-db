-- Verify gwapo-db:guild_upgrade_lang on pg
BEGIN;

SELECT
  app_name,
  guild_upgrade_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.guild_upgrade_description
WHERE
  FALSE;

SELECT
  app_name,
  guild_upgrade_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.guild_upgrade_description_history
WHERE
  FALSE;

SELECT
  app_name,
  guild_upgrade_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.guild_upgrade_description_context
WHERE
  FALSE;

SELECT
  app_name,
  guild_upgrade_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.guild_upgrade_description_context_history
WHERE
  FALSE;

SELECT
  app_name,
  guild_upgrade_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.guild_upgrade_name
WHERE
  FALSE;

SELECT
  app_name,
  guild_upgrade_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.guild_upgrade_name_history
WHERE
  FALSE;

SELECT
  app_name,
  guild_upgrade_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.guild_upgrade_name_context
WHERE
  FALSE;

SELECT
  app_name,
  guild_upgrade_id,
  original_lang_tag,
  original,
  sysrange_lower,
  sysrange_upper,
  translation_lang_tag,
  translation
FROM
  gwapese.guild_upgrade_name_context_history
WHERE
  FALSE;

ROLLBACK;
