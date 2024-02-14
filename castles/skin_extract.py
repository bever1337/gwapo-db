import datetime
import luigi

import common
from tasks import extract_batch
from tasks import extract_id


skin_url = "https://api.guildwars2.com/v2/skins"
skin_json_schema_path = "./schema/gw2/v2/skins/index.json"


class ExtractId(extract_id.ExtractIdTask):
    json_schema_path = skin_json_schema_path
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "skin"
    url = skin_url


class ExtractBatch(extract_batch.ExtractBatchTask):
    json_schema_path = skin_json_schema_path
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "skin"
    url = skin_url

    @property
    def url_params(self):
        return {"lang": self.lang_tag.value}

    def requires(self):
        return ExtractId()
