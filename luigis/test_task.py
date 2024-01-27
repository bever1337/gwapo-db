import datetime
import luigi
from os import path

import common
import extract_batch


class TestTask(extract_batch.ExtractBatch):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)

    entity_schema = "../schema/gw2/v2/novelties/novelty.json"
    extract_dir = "extract_test_id"
    id_schema = "../schema/gw2/v2/novelties/index.json"
    output_file = "extract_test"
    url_params = {"lang": common.LangTag.En.value}
    url = "https://api.guildwars2.com/v2/novelties"
