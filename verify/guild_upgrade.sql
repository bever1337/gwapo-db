-- Verify gwapo-db:guild_upgrade on pg
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
  guild_upgrade_id,
  prerequisite_guild_upgrade_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.guild_upgrade_prerequisite
WHERE
  FALSE;

SELECT
  guild_upgrade_id,
  prerequisite_guild_upgrade_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.guild_upgrade_prerequisite_history
WHERE
  FALSE;

ROLLBACK;
