-- Verify gwapo-db:guild_currency on pg
BEGIN;

SELECT
  guild_currency_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.guild_currency
WHERE
  FALSE;

SELECT
  guild_currency_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.guild_currency_history
WHERE
  FALSE;

SELECT
  app_name,
  guild_currency_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.guild_currency_description
WHERE
  FALSE;

SELECT
  app_name,
  guild_currency_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.guild_currency_description_history
WHERE
  FALSE;

SELECT
  app_name,
  guild_currency_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.guild_currency_name
WHERE
  FALSE;

SELECT
  app_name,
  guild_currency_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.guild_currency_name_history
WHERE
  FALSE;

ROLLBACK;
