import luigi

import common
from tasks import config
from tasks import extract_batch
from tasks import extract_id


specialization_url = "https://api.guildwars2.com/v2/specializations"
specialization_json_schema_path = "./schema/gw2/v2/specializations/index.json"


class ExtractId(extract_id.ExtractIdTask):
    json_schema_path = specialization_json_schema_path
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "specialization"
    url = specialization_url


class ExtractBatch(extract_batch.ExtractBatchTask):
    json_schema_path = specialization_json_schema_path
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "specialization"
    url = specialization_url

    @property
    def url_params(self):
        return {"lang": self.lang_tag.value}

    def requires(self):
        return ExtractId()
