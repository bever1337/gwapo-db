-- Revert gwapo-db:guild_upgrade_cost from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'guild_upgrade_cost_currency');

DROP TABLE gwapese.guild_upgrade_cost_currency_history;

DROP TABLE gwapese.guild_upgrade_cost_currency;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'guild_upgrade_cost_item');

DROP TABLE gwapese.guild_upgrade_cost_item_history;

DROP TABLE gwapese.guild_upgrade_cost_item;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'guild_upgrade_cost_wallet');

DROP TABLE gwapese.guild_upgrade_cost_wallet_history;

DROP TABLE gwapese.guild_upgrade_cost_wallet;

COMMIT;
