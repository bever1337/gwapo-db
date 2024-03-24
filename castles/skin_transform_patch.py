from os import path
import luigi

import common
import skin_extract
from tasks import config
from tasks import transform_patch


class TransformPatch(transform_patch.TransformPatchTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "skin"

    @property
    def json_patch_path(self):
        patch_filename = "skin_de" if self.lang_tag == common.LangTag.De else "noop"
        patch_filename_ext = path.extsep.join([patch_filename, "json"])
        patch_path = path.sep.join(["patch", patch_filename_ext])
        return patch_path

    def requires(self):
        return skin_extract.ExtractBatch(lang_tag=self.lang_tag)
