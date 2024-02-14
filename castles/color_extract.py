import datetime
import luigi

import common
from tasks import extract_batch
from tasks import extract_id


color_url = "https://api.guildwars2.com/v2/colors"
color_json_schema_path = "./schema/gw2/v2/colors/index.json"


class ExtractId(extract_id.ExtractIdTask):
    json_schema_path = color_json_schema_path
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "color"
    url = color_url


class ExtractBatch(extract_batch.ExtractBatchTask):
    json_schema_path = color_json_schema_path
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "color"
    url = color_url

    @property
    def url_params(self):
        return {"lang": self.lang_tag.value}

    def requires(self):
        return ExtractId()
