import datetime
import luigi

import common
from tasks import extract_batch
from tasks import extract_id


currency_url = "https://api.guildwars2.com/v2/currencies"
currency_json_schema_path = "./schema/gw2/v2/currencies/index.json"


class ExtractId(extract_id.ExtractIdTask):
    json_schema_path = currency_json_schema_path
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "currency"
    url = currency_url


class ExtractBatch(extract_batch.ExtractBatchTask):
    json_schema_path = currency_json_schema_path
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "currency"
    url = currency_url

    @property
    def url_params(self):
        return {"lang": self.lang_tag.value}

    def requires(self):
        return ExtractId()
