import datetime
import luigi

import common
import mini_extract
from tasks import transform_patch


class TransformPatch(transform_patch.TransformPatchTask):
    json_patch_path = "./patch/mini.json"
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "mini"

    def requires(self):
        return mini_extract.ExtractBatch(lang_tag=self.lang_tag)
