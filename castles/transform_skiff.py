import luigi

import common
import extract_batch
import transform_csv
import transform_lang


class TransformSkiffTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        return extract_batch.ExtractBatchTask(
            json_schema_path="./schema/gw2/v2/skiffs/index.json",
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/skiffs",
        )


class TransformSkiff(TransformSkiffTask):
    def get_rows(self, skiff):
        return [{"icon": skiff["icon"], "skiff_id": skiff["id"]}]


class TransformSkiffDyeSlot(TransformSkiffTask):
    def get_rows(self, skiff):
        skiff_id = skiff["id"]
        return [
            {
                "color_id": dye_slot["color_id"],
                "material": dye_slot["material"],
                "skiff_id": skiff_id,
                "slot_index": slot_index,
            }
            for slot_index, dye_slot in enumerate(skiff["dye_slots"])
        ]


class TransformSkiffName(TransformSkiffTask):
    def get_rows(self, skiff):
        return [
            {
                "app_name": "gw2",
                "lang_tag": self.lang_tag.value,
                "original": transform_lang.to_xhmtl_fragment(skiff["name"]),
                "skiff_id": skiff["id"],
            }
        ]
