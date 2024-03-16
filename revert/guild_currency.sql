-- Revert gwapo-db:guild_currency from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'guild_currency');

DROP TABLE gwapese.guild_currency_history;

DROP TABLE gwapese.guild_currency;

COMMIT;
