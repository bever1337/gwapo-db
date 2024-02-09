-- Deploy gwapo-db:guild_upgrade_cost to pg
-- requires: schema
-- requires: history
-- requires: currency
-- requires: guild_currency
-- requires: guild_upgrade
-- requires: item
BEGIN;

CREATE TABLE gwapese.guild_upgrade_cost_currency (
  guild_currency_id text NOT NULL,
  guild_upgrade_id integer NOT NULL,
  quantity integer NOT NULL,
  CONSTRAINT guild_upgrade_cost_currency_pk PRIMARY KEY (guild_upgrade_id,
    guild_currency_id),
  CONSTRAINT guild_currency_identifies_guild_upgrade_cost_currency_fk FOREIGN
    KEY (guild_currency_id) REFERENCES gwapese.guild_currency
    (guild_currency_id),
  CONSTRAINT guild_upgrade_identifies_guild_upgrade_cost_currency_fk FOREIGN
    KEY (guild_upgrade_id) REFERENCES gwapese.guild_upgrade (guild_upgrade_id)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'guild_upgrade_cost_currency');

CREATE TABLE gwapese.guild_upgrade_cost_currency_history (
  LIKE gwapese.guild_upgrade_cost_currency
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'guild_upgrade_cost_currency', 'guild_upgrade_cost_currency_history');

CREATE TABLE gwapese.guild_upgrade_cost_item (
  guild_upgrade_id integer NOT NULL,
  item_id integer NOT NULL,
  quantity integer NOT NULL,
  CONSTRAINT guild_upgrade_cost_item_pk PRIMARY KEY (guild_upgrade_id, item_id),
  CONSTRAINT guild_upgrade_identifies_guild_upgrade_cost_item_fk FOREIGN KEY
    (guild_upgrade_id) REFERENCES gwapese.guild_upgrade (guild_upgrade_id),
  CONSTRAINT item_identifies_guild_upgrade_cost_item_fk FOREIGN KEY (item_id)
    REFERENCES gwapese.item (item_id)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'guild_upgrade_cost_item');

CREATE TABLE gwapese.guild_upgrade_cost_item_history (
  LIKE gwapese.guild_upgrade_cost_item
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'guild_upgrade_cost_item', 'guild_upgrade_cost_item_history');

CREATE TABLE gwapese.guild_upgrade_cost_wallet (
  currency_id integer NOT NULL,
  guild_upgrade_id integer NOT NULL,
  quantity integer NOT NULL,
  CONSTRAINT guild_upgrade_cost_coin_pk PRIMARY KEY (guild_upgrade_id, currency_id),
  CONSTRAINT currency_identifies_guild_upgrade_cost_wallet_fk FOREIGN KEY
    (currency_id) REFERENCES gwapese.currency (currency_id),
  CONSTRAINT guild_upgrade_identifies_guild_upgrade_cost_wallet_fk FOREIGN KEY
    (guild_upgrade_id) REFERENCES gwapese.guild_upgrade (guild_upgrade_id)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'guild_upgrade_cost_wallet');

CREATE TABLE gwapese.guild_upgrade_cost_wallet_history (
  LIKE gwapese.guild_upgrade_cost_wallet
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'guild_upgrade_cost_wallet', 'guild_upgrade_cost_wallet_history');

COMMIT;
