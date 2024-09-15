-- Verify gwapo-db:currency_exchange on pg
BEGIN;

SELECT
  coin,
  coins,
  coins_per_gem,
  gem,
  gems,
  recorded,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.currency_exchange_coin
WHERE
  FALSE;

SELECT
  coin,
  coins,
  coins_per_gem,
  gem,
  gems,
  recorded,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.currency_exchange_coin_history
WHERE
  FALSE;

SELECT
  coin,
  coins,
  coins_per_gem,
  gem,
  gems,
  recorded,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.currency_exchange_gem
WHERE
  FALSE;

SELECT
  coin,
  coins,
  coins_per_gem,
  gem,
  gems,
  recorded,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.currency_exchange_gem_history
WHERE
  FALSE;

ROLLBACK;
