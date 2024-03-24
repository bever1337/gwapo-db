import luigi

import common
from tasks import config
from tasks import extract_batch
from tasks import extract_id


profession_url = "https://api.guildwars2.com/v2/professions"
profession_json_schema_path = "./schema/gw2/v2/professions/index.json"


class ExtractId(extract_id.ExtractIdTask):
    json_schema_path = profession_json_schema_path
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "profession"
    url = profession_url


class ExtractBatch(extract_batch.ExtractBatchTask):
    json_schema_path = profession_json_schema_path
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "profession"
    url = profession_url

    @property
    def url_params(self):
        return {"lang": self.lang_tag.value, "v": "2019-12-19T00:00:00.000Z"}

    def requires(self):
        return ExtractId()
