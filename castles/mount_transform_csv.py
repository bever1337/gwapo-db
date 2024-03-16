import luigi

import common
import mount_extract
from tasks import config
from tasks import transform_csv


class TransformCsvMountTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "mount"

    def requires(self):
        return mount_extract.ExtractBatch(lang_tag=self.lang_tag)


class TransformCsvMount(TransformCsvMountTask):
    def get_rows(self, mount):
        return [{"mount_id": mount["id"]}]


class TransformCsvMountSkinDefault(TransformCsvMountTask):
    def get_rows(self, mount):
        return [{"mount_id": mount["id"], "mount_skin_id": mount["default_skin"]}]


class TransformCsvMountName(TransformCsvMountTask):
    def get_rows(self, mount):
        return [
            {
                "app_name": "gw2",
                "mount_id": mount["id"],
                "lang_tag": self.lang_tag.value,
                "original": common.to_xhmtl_fragment(mount["name"]),
            }
        ]


class TransformCsvMountNameTranslation(transform_csv.TransformCsvTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "mount"
    translation_lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def get_rows(self, mount):
        return [
            {
                "app_name": self.app_name,
                "mount_id": mount["id"],
                "original_lang_tag": self.original_lang_tag.value,
                "translation_lang_tag": self.translation_lang_tag.value,
                "translation": common.to_xhmtl_fragment(mount["name"]),
            }
        ]

    def requires(self):
        return mount_extract.ExtractBatch(lang_tag=self.translation_lang_tag)
