import luigi

import color_extract
import common
from tasks import config
from tasks import transform_patch


class TransformPatch(transform_patch.TransformPatchTask):
    json_patch_path = "./patch/color.json"
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "color"

    def requires(self):
        return color_extract.ExtractBatch(lang_tag=self.lang_tag)
