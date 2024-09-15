-- Deploy gwapo-db:currency_exchange to pg
-- requires: schema
-- requires: history
-- requires: currency
BEGIN;

CREATE TABLE gwapese.currency_exchange_coin (
  coin integer NOT NULL,
  coins integer NOT NULL,
  coins_per_gem integer NOT NULL,
  gem integer NOT NULL,
  gems integer NOT NULL,
  recorded timestamptz(3) NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT currency_exchange_coin_pk PRIMARY KEY (coin, gem, coins, recorded),
  CONSTRAINT currency_exchange_coin_u UNIQUE (coins, recorded),
  CONSTRAINT currency_identifies_exchange_coin_coin_fk FOREIGN KEY (coin)
    REFERENCES gwapese.currency (currency_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT currency_identifies_exchange_coin_gem_fk FOREIGN KEY (gem)
    REFERENCES gwapese.currency (currency_id) ON DELETE CASCADE ON UPDATE
    CASCADE
);

CREATE TABLE gwapese.currency_exchange_coin_history (
  LIKE gwapese.currency_exchange_coin
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'currency_exchange_coin', 'currency_exchange_coin_history');

CREATE TABLE gwapese.currency_exchange_gem (
  LIKE gwapese.currency_exchange_coin,
  CONSTRAINT currency_exchange_gem_pk PRIMARY KEY (gem, coin, gems, recorded),
  CONSTRAINT currency_exchange_gem_u UNIQUE (gems, recorded),
  CONSTRAINT currency_identifies_exchange_gem_coin_fk FOREIGN KEY (coin)
    REFERENCES gwapese.currency (currency_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT currency_identifies_exchange_gem_gem_fk FOREIGN KEY (gem)
    REFERENCES gwapese.currency (currency_id) ON DELETE CASCADE ON UPDATE
    CASCADE
);

CREATE TABLE gwapese.currency_exchange_gem_history (
  LIKE gwapese.currency_exchange_gem
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'currency_exchange_gem', 'currency_exchange_gem_history');

COMMIT;

-- Live example
-- SELECT *
-- FROM gwapese.currency_exchange_gem
-- WHERE gwapese.currency_exchange_gem.recorded = (
--   SELECT MAX(recorded)
--   FROM gwapese.currency_exchange_gem
-- );
--
--
-- Candlestick example
-- SELECT DISTINCT bucket.a,
--   bucket.b,
--   bucket.bucket_time,
--   MAX(bucket.recorded) OVER bucket_w AS "close",
--   LAST_VALUE(bucket.record_rate) OVER bucket_w AS "close_rate",
--   MAX(bucket.record_rate) OVER bucket_w AS "high",
--   MIN(bucket.record_rate) OVER bucket_w AS "low",
--   MIN(bucket.recorded) OVER bucket_w AS "open",
--   FIRST_VALUE(bucket.record_rate) OVER bucket_w AS "open_rate"
-- FROM (
--   SELECT date_trunc('hour', gwapese.currency_exchange_gem.recorded) as "bucket_time",
--     recorded,
--     gem AS "a",
--     coin AS "b",
--     CEILING(CAST((SUM(coins) OVER record_w) AS decimal) / CAST((SUM(gems) OVER record_w) AS decimal)) AS "record_rate"
--   FROM gwapese.currency_exchange_gem
--   WINDOW record_w AS (PARTITION BY gwapese.currency_exchange_gem.recorded)
-- ) AS "bucket"
-- WINDOW bucket_w AS (PARTITION BY bucket.bucket_time)
-- ORDER BY bucket.bucket_time;
