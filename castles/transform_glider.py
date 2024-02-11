import luigi

import common
import extract_batch
import transform_csv
import transform_lang


class TransformGliderTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        return extract_batch.ExtractBatchTask(
            json_schema_path="./schema/gw2/v2/gliders/index.json",
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/gliders",
        )


class TransformGlider(TransformGliderTask):
    def get_rows(self, glider):
        return [
            {
                "glider_id": glider["id"],
                "icon": glider["icon"],
                "presentation_order": glider["order"],
            }
        ]


class TransformGliderDescription(TransformGliderTask):
    def get_rows(self, glider):
        glider_description = glider["description"]
        if glider_description == "":
            return []
        return [
            {
                "app_name": "gw2",
                "glider_id": glider["id"],
                "lang_tag": self.lang_tag.value,
                "original": transform_lang.to_xhmtl_fragment(glider_description),
            }
        ]


class TransformGliderDyeSlot(TransformGliderTask):
    def get_rows(self, glider):
        glider_id = glider["id"]
        return [
            {
                "color_id": color_id,
                "glider_id": glider_id,
                "slot_index": index,
            }
            for index, color_id in enumerate(glider["default_dyes"])
        ]


class TransformGliderItem(TransformGliderTask):
    def get_rows(self, glider):
        glider_id = glider["id"]
        return [
            {"glider_id": glider_id, "item_id": item_id}
            for item_id in glider.get("unlock_items", [])
        ]


class TransformGliderName(TransformGliderTask):
    def get_rows(self, glider):
        return [
            {
                "app_name": "gw2",
                "glider_id": glider["id"],
                "lang_tag": self.lang_tag.value,
                "original": transform_lang.to_xhmtl_fragment(glider["name"]),
            }
        ]
