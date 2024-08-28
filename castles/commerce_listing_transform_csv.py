import luigi

import commerce_listing_extract
from tasks import config
from tasks import transform_csv


class TransformCsvCommerceListingTask(transform_csv.TransformCsvTask):
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "commerce"

    def requires(self):
        return commerce_listing_extract.ExtractBatch()


class TransformCsvCommerceListingBuy(TransformCsvCommerceListingTask):
    def get_rows(self, listings):
        return [
            {
                "item_id": listings["id"],
                "listings": listing["listings"],
                "quantity": listing["quantity"],
                "recorded": self.task_datetime,
                "unit_price": listing["unit_price"],
            }
            for listing in listings["buys"]
        ]


class TransformCsvCommerceListingSell(TransformCsvCommerceListingTask):
    def get_rows(self, listings):
        return [
            {
                "item_id": listings["id"],
                "listings": listing["listings"],
                "quantity": listing["quantity"],
                "recorded": self.task_datetime,
                "unit_price": listing["unit_price"],
            }
            for listing in listings["sells"]
        ]
