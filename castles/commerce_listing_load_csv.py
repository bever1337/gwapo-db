import luigi
from psycopg import sql

import commerce_listing_transform_csv
from tasks import config
from tasks import load_csv


class WrapCommerceListing(luigi.WrapperTask):
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        args = {"task_datetime": self.task_datetime}
        yield LoadCsvCommerceListingBuy(**args)
        yield LoadCsvCommerceListingSell(**args)


class LoadCsvCommerceListingTask(load_csv.LoadCsvTask):
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "commerce"


class LoadCsvCommerceListingBuy(LoadCsvCommerceListingTask):
    table = "commerce_listing_buy"

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM ONLY
  tempo_commerce_listing_buy
USING
  tempo_commerce_listing_buy
AS
  tclb
LEFT JOIN
  gwapese.item
AS
  i
ON
  tclb.item_id = i.item_id
WHERE
  tempo_commerce_listing_buy.item_id = tclb.item_id
  AND tempo_commerce_listing_buy.recorded = tclb.recorded
  AND tempo_commerce_listing_buy.unit_price = tclb.unit_price
  AND i.item_id IS NULL;
"""
            ),
            sql.SQL(
                """
MERGE INTO
  gwapese.commerce_listing_buy
AS
  target_commerce_listing_buy
USING (
  SELECT DISTINCT ON
    (item_id, recorded, unit_price)
    item_id, listings, quantity, recorded, unit_price
  FROM tempo_commerce_listing_buy)
AS
  source_commerce_listing_buy
ON
  target_commerce_listing_buy.item_id = source_commerce_listing_buy.item_id AND
  target_commerce_listing_buy.recorded = source_commerce_listing_buy.recorded AND
  target_commerce_listing_buy.unit_price = source_commerce_listing_buy.unit_price
WHEN MATCHED AND
  source_commerce_listing_buy.listings != target_commerce_listing_buy.listings
  OR source_commerce_listing_buy.quantity != target_commerce_listing_buy.quantity
THEN
  UPDATE SET (listings, quantity) =
    (source_commerce_listing_buy.listings, source_commerce_listing_buy.quantity)
WHEN NOT MATCHED THEN
  INSERT (item_id, listings, quantity, recorded, unit_price)
    VALUES (source_commerce_listing_buy.item_id, source_commerce_listing_buy.listings,
      source_commerce_listing_buy.quantity, source_commerce_listing_buy.recorded,
      source_commerce_listing_buy.unit_price);
"""
            ),
        ]
    )

    def requires(self):
        return {
            self.table: commerce_listing_transform_csv.TransformCsvCommerceListingBuy()
        }


class LoadCsvCommerceListingSell(LoadCsvCommerceListingTask):
    table = "commerce_listing_sell"

    postcopy_sql = sql.Composed(
        [
            sql.SQL(
                """
DELETE FROM ONLY
  tempo_commerce_listing_sell
USING
  tempo_commerce_listing_sell
AS
  tcls
LEFT JOIN
  gwapese.item
AS
  i
ON
  tcls.item_id = i.item_id
WHERE
  tempo_commerce_listing_sell.item_id = tcls.item_id
  AND tempo_commerce_listing_sell.recorded = tcls.recorded
  AND tempo_commerce_listing_sell.unit_price = tcls.unit_price
  AND i.item_id IS NULL;
"""
            ),
            sql.SQL(
                """
MERGE INTO
  gwapese.commerce_listing_sell
AS
  target_commerce_listing_sell
USING (
  SELECT DISTINCT ON
    (item_id, recorded, unit_price)
    item_id, listings, quantity, recorded, unit_price
  FROM tempo_commerce_listing_sell)
AS
  source_commerce_listing_sell
ON
  target_commerce_listing_sell.item_id = source_commerce_listing_sell.item_id AND
  target_commerce_listing_sell.recorded = source_commerce_listing_sell.recorded AND
  target_commerce_listing_sell.unit_price = source_commerce_listing_sell.unit_price
WHEN MATCHED AND
  source_commerce_listing_sell.listings != target_commerce_listing_sell.listings
  OR source_commerce_listing_sell.quantity != target_commerce_listing_sell.quantity
THEN
  UPDATE SET (listings, quantity) =
    (source_commerce_listing_sell.listings, source_commerce_listing_sell.quantity)
WHEN NOT MATCHED THEN
  INSERT (item_id, listings, quantity, recorded, unit_price)
    VALUES (source_commerce_listing_sell.item_id, source_commerce_listing_sell.listings,
      source_commerce_listing_sell.quantity, source_commerce_listing_sell.recorded,
      source_commerce_listing_sell.unit_price);
"""
            ),
        ]
    )

    def requires(self):
        return {
            self.table: commerce_listing_transform_csv.TransformCsvCommerceListingSell()
        }
