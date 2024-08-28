import luigi

import common
from tasks import config
from tasks import extract_batch
from tasks import extract_id


commerce_listings_url = "https://api.guildwars2.com/v2/commerce/listings"
commerce_listings_json_schema_path = "./schema/gw2/v2/commerce/listings.json"


class ExtractId(extract_id.ExtractIdTask):
    json_schema_path = commerce_listings_json_schema_path
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "commerce"
    url = commerce_listings_url


class ExtractBatch(extract_batch.ExtractBatchTask):
    json_schema_path = commerce_listings_json_schema_path
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "commerce"
    url = commerce_listings_url

    @property
    def url_params(self):
        return {}

    def requires(self):
        return ExtractId()
