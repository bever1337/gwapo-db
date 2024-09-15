import enum
import luigi
from psycopg import sql

import currency_exchange_extract
from tasks import config
from tasks import load_csv


class WrapCurrencyExchange(luigi.WrapperTask):
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        args = {"task_datetime": self.task_datetime}
        yield LoadCsvCurrencyExchangeCoin(**args)
        yield LoadCsvCurrencyExchangeGem(**args)


class LoadCsvCurrencyExchangeTask(load_csv.LoadCsvTask):
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "currency_exchange"


class LoadCsvCurrencyExchangeCoin(LoadCsvCurrencyExchangeTask):
    table = "currency_exchange_coin"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.currency_exchange_coin
  AS target_currency_exchange_coin
USING tempo_currency_exchange_coin
  AS source_currency_exchange_coin
ON target_currency_exchange_coin.coin = source_currency_exchange_coin.coin
  AND target_currency_exchange_coin.coins = source_currency_exchange_coin.coins
  AND target_currency_exchange_coin.gem = source_currency_exchange_coin.gem
  AND target_currency_exchange_coin.gems = source_currency_exchange_coin.gems
  AND target_currency_exchange_coin.recorded = source_currency_exchange_coin.recorded
WHEN MATCHED AND target_currency_exchange_coin.coins_per_gem
  != source_currency_exchange_coin.coins_per_gem
THEN UPDATE SET
  coins_per_gem = source_currency_exchange_coin.coins_per_gem
WHEN NOT MATCHED THEN INSERT (
    coin, coins, coins_per_gem, gem, gems, recorded
  ) VALUES (
    source_currency_exchange_coin.coin,
    source_currency_exchange_coin.coins,
    source_currency_exchange_coin.coins_per_gem,
    source_currency_exchange_coin.gem,
    source_currency_exchange_coin.gems,
    source_currency_exchange_coin.recorded);
"""
    )

    def requires(self):
        return {
            self.table: currency_exchange_extract.ExtractCurrencyExchange(
                atob=currency_exchange_extract.Atob.Coins
            )
        }


class LoadCsvCurrencyExchangeGem(LoadCsvCurrencyExchangeTask):
    table = "currency_exchange_gem"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.currency_exchange_gem
  AS target_currency_exchange_gem
USING tempo_currency_exchange_gem
  AS source_currency_exchange_gem
ON target_currency_exchange_gem.coin = source_currency_exchange_gem.coin
  AND target_currency_exchange_gem.coins = source_currency_exchange_gem.coins
  AND target_currency_exchange_gem.gem = source_currency_exchange_gem.gem
  AND target_currency_exchange_gem.gems = source_currency_exchange_gem.gems
  AND target_currency_exchange_gem.recorded = source_currency_exchange_gem.recorded
WHEN MATCHED AND target_currency_exchange_gem.coins_per_gem
  != source_currency_exchange_gem.coins_per_gem
THEN UPDATE SET
  coins_per_gem = source_currency_exchange_gem.coins_per_gem
WHEN NOT MATCHED THEN INSERT (
    coin, coins, coins_per_gem, gem, gems, recorded)
  VALUES (
    source_currency_exchange_gem.coin,
    source_currency_exchange_gem.coins,
    source_currency_exchange_gem.coins_per_gem,
    source_currency_exchange_gem.gem,
    source_currency_exchange_gem.gems,
    source_currency_exchange_gem.recorded);
"""
    )

    def requires(self):
        return {
            self.table: currency_exchange_extract.ExtractCurrencyExchange(
                atob=currency_exchange_extract.Atob.Gems
            )
        }
