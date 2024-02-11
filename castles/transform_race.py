import luigi

import common
import extract_batch
import transform_csv
import transform_lang


class TransformRaceTask(transform_csv.TransformCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        return extract_batch.ExtractBatchTask(
            json_schema_path="./schema/gw2/v2/races/index.json",
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/races",
        )


class TransformRace(TransformRaceTask):
    def get_rows(self, race):
        return [{"race_id": race["id"]}]


class TransformRaceName(TransformRaceTask):
    def get_rows(self, race):
        return [
            {
                "app_name": "gw2",
                "lang_tag": self.lang_tag.value,
                "original": transform_lang.to_xhmtl_fragment(race["name"]),
                "race_id": race["id"],
            }
        ]
