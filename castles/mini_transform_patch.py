from os import path
import luigi

import common
import mini_extract
from tasks import config
from tasks import transform_patch


class TransformPatch(transform_patch.TransformPatchTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "mini"

    @property
    def json_patch_path(self):
        patch_filename = "_".join(["./patch/mini", self.lang_tag.value])
        patch_filename_ext = path.extsep.join([patch_filename, "json"])
        return patch_filename_ext

    def requires(self):
        return mini_extract.ExtractBatch(lang_tag=self.lang_tag)
