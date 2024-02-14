import datetime
import luigi

import common
import currency_extract
from tasks import transform_patch


class TransformPatch(transform_patch.TransformPatchTask):
    json_patch_path = "./patch/currency.json"
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "currency"

    def requires(self):
        return currency_extract.ExtractBatch(lang_tag=self.lang_tag)
