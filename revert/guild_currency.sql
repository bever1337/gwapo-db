-- Revert gwapo-db:guild_currency from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'guild_currency_description');

DROP TABLE gwapese.guild_currency_description_history;

DROP TABLE gwapese.guild_currency_description;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'guild_currency_name');

DROP TABLE gwapese.guild_currency_name_history;

DROP TABLE gwapese.guild_currency_name;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'guild_currency');

DROP TABLE gwapese.guild_currency_history;

DROP TABLE gwapese.guild_currency;

COMMIT;
