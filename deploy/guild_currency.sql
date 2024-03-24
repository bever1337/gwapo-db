-- Deploy gwapo-db:guild_currency to pg
-- requires: schema
-- requires: history
BEGIN;

CREATE TABLE gwapese.guild_currency (
  guild_currency_id text NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT guild_currency_pk PRIMARY KEY (guild_currency_id)
);

CREATE TABLE gwapese.guild_currency_history (
  LIKE gwapese.guild_currency
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'guild_currency', 'guild_currency_history');

COMMIT;
