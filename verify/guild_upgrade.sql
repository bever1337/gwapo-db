-- Verify gawpo-db:guild_upgrade on pg
BEGIN;

SELECT
  build_time,
  experience,
  guild_upgrade_id,
  guild_upgrade_type,
  icon,
  required_level,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.guild_upgrade
WHERE
  FALSE;

SELECT
  build_time,
  experience,
  guild_upgrade_id,
  guild_upgrade_type,
  icon,
  required_level,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.guild_upgrade_history
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

ROLLBACK;
