import luigi

import common
import extract_batch
import transform_patch


class TransformPatchColor(transform_patch.TransformPatchTask):
    json_patch_path = "./patch/color.json"
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        return extract_batch.ExtractBatchTask(
            json_schema_path="./schema/gw2/v2/colors/index.json",
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/colors",
        )
