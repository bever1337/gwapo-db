import luigi

from tasks import config
from tasks import extract_batch
from tasks import extract_id

emote_url = "https://api.guildwars2.com/v2/emotes"
emote_json_schema_path = "./schema/gw2/v2/emotes/index.json"


class ExtractId(extract_id.ExtractIdTask):
    json_schema_path = emote_json_schema_path
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "emote"
    url = emote_url


class ExtractBatch(extract_batch.ExtractBatchTask):
    json_schema_path = emote_json_schema_path
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "emote"
    url_params = {}
    url = emote_url

    def requires(self):
        return ExtractId()
