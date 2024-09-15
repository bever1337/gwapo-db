-- Revert gwapo-db:currency_exchange from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'currency_exchange_coin');

DROP TABLE gwapese.currency_exchange_coin_history;

DROP TABLE gwapese.currency_exchange_coin;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'currency_exchange_gem');

DROP TABLE gwapese.currency_exchange_gem_history;

DROP TABLE gwapese.currency_exchange_gem;

COMMIT;
