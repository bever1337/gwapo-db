import luigi

import common
import transform_csv
import transform_lang
import transform_patch_mini


class TransformMiniTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        return transform_patch_mini.TransformPatchMini(lang_tag=self.lang_tag)


class TransformMini(TransformMiniTask):
    def get_rows(self, mini):
        return [
            {
                "icon": mini["icon"],
                "mini_id": mini["id"],
                "presentation_order": mini["order"],
            }
        ]


class TransformMiniItem(TransformMiniTask):
    def get_rows(self, mini):
        return [{"item_id": mini["item_id"], "mini_id": mini["id"]}]


class TransformMiniName(TransformMiniTask):
    def get_rows(self, mini):
        return [
            {
                "app_name": "gw2",
                "lang_tag": self.lang_tag.value,
                "mini_id": mini["id"],
                "original": transform_lang.to_xhmtl_fragment(mini["name"]),
            }
        ]


class TransformMiniUnlock(TransformMiniTask):
    def get_rows(self, mini):
        mini_unlock = mini.get("unlock")
        if mini_unlock == None:
            return []
        return [
            {
                "app_name": "gw2",
                "lang_tag": self.lang_tag.value,
                "mini_id": mini["id"],
                "original": transform_lang.to_xhmtl_fragment(mini_unlock),
            }
        ]
