-- Verify gwapo-db:guild_upgrade_cost on pg
BEGIN;

SELECT
  guild_currency_id,
  guild_upgrade_id,
  quantity,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.guild_upgrade_cost_currency
WHERE
  FALSE;

SELECT
  guild_currency_id,
  guild_upgrade_id,
  quantity,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.guild_upgrade_cost_currency_history
WHERE
  FALSE;

SELECT
  guild_upgrade_id,
  item_id,
  quantity,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.guild_upgrade_cost_item
WHERE
  FALSE;

SELECT
  guild_upgrade_id,
  item_id,
  quantity,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.guild_upgrade_cost_item_history
WHERE
  FALSE;

SELECT
  currency_id,
  guild_upgrade_id,
  quantity,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.guild_upgrade_cost_wallet
WHERE
  FALSE;

SELECT
  currency_id,
  guild_upgrade_id,
  quantity,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.guild_upgrade_cost_wallet_history
WHERE
  FALSE;

ROLLBACK;
