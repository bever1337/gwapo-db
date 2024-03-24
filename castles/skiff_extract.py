import luigi

import common
from tasks import config
from tasks import extract_batch
from tasks import extract_id


skiff_url = "https://api.guildwars2.com/v2/skiffs"
skiff_json_schema_path = "./schema/gw2/v2/skiffs/index.json"


class ExtractId(extract_id.ExtractIdTask):
    json_schema_path = skiff_json_schema_path
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "skiff"
    url = skiff_url


class ExtractBatch(extract_batch.ExtractBatchTask):
    json_schema_path = skiff_json_schema_path
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "skiff"
    url = skiff_url

    @property
    def url_params(self):
        return {"lang": self.lang_tag.value}

    def requires(self):
        return ExtractId()
