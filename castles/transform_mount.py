import luigi

import common
import extract_batch
import transform_csv
import transform_lang


class TransformMountTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        return extract_batch.ExtractBatchTask(
            json_schema_path="./schema/gw2/v2/mounts/types/index.json",
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/mounts/types",
        )


class TransformMount(TransformMountTask):
    def get_rows(self, mount):
        return [{"mount_id": mount["id"]}]


class TransformMountSkinDefault(TransformMountTask):
    def get_rows(self, mount):
        return [{"mount_id": mount["id"], "mount_skin_id": mount["default_skin"]}]


class TransformMountName(TransformMountTask):
    def get_rows(self, mount):
        return [
            {
                "app_name": "gw2",
                "mount_id": mount["id"],
                "lang_tag": self.lang_tag.value,
                "original": transform_lang.to_xhmtl_fragment(mount["name"]),
            }
        ]
