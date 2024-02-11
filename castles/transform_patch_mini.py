import luigi

import common
import extract_batch
import transform_patch


class TransformPatchMini(transform_patch.TransformPatchTask):
    json_patch_path = "./patch/mini.json"
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        return extract_batch.ExtractBatchTask(
            json_schema_path="./schema/gw2/v2/minis/index.json",
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/minis",
        )
