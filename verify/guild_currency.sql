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

ROLLBACK;
