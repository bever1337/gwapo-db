import datetime
import json
import luigi
from os import path

import common
import extract_batch
import load_lang


class LoadSkiff(luigi.Task):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)

    def output(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.txt".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        target_path = path.join(
            self.output_dir,
            "load_skiff",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.json".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        return extract_batch.ExtractBatch(
            entity_schema="../schema/gw2/v2/skiffs/skiff.json",
            extract_datetime=self.extract_datetime,
            extract_dir=path.join(self.output_dir, "extract_skiff_id"),
            id_schema="../schema/gw2/v2/skiffs/index.json",
            output_file=path.join(
                self.output_dir,
                "extract_skiff",
                target_filename,
            ),
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/skiffs",
        )

    def run(self):
        with self.input().open("r") as ro_input_file:
            json_input = json.load(fp=ro_input_file)

        with (
            common.get_conn() as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute(query="BEGIN")
            try:
                for skiff in json_input:
                    skiff_id = skiff["id"]
                    cursor.execute(
                        **upsert_skiff(skiff_id=skiff_id, icon=skiff["icon"])
                    )

                    skiff_dye_slots: list[dict] = skiff["dye_slots"]
                    slot_indices = [index for index in range(len(skiff_dye_slots))]
                    cursor.execute(
                        **prune_skiff_dye_slots(
                            skiff_id=skiff_id, slot_indices=slot_indices
                        )
                    )
                    for slot_index, dye_slot in enumerate(skiff_dye_slots):
                        cursor.execute(
                            **upsert_skiff_dye_slots(
                                color_id=dye_slot["color_id"],
                                material=dye_slot["material"],
                                skiff_id=skiff_id,
                                slot_index=slot_index,
                            )
                        )

                    skiff_name = skiff["name"]
                    cursor.execute(
                        **load_lang.upsert_operating_copy(
                            app_name="gw2",
                            lang_tag=self.lang_tag.value,
                            original=skiff_name,
                        )
                    )
                    cursor.execute(
                        **upsert_skiff_name(
                            app_name="gw2",
                            skiff_id=skiff_id,
                            lang_tag=self.lang_tag.value,
                            original=skiff_name,
                        )
                    )

                cursor.execute(query="COMMIT")
                connection.commit()
                with self.output().open("w") as w_output:
                    w_output.write("ok")

            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                raise exception_instance


def upsert_skiff(icon: str, skiff_id: int) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.skiff AS target_skiff
USING (
  VALUES (%(icon)s::text, %(skiff_id)s::integer)
) AS source_skiff (icon, skiff_id)
ON
  target_skiff.skiff_id = source_skiff.skiff_id
WHEN MATCHED
  AND target_skiff.icon != source_skiff.icon THEN
  UPDATE SET
    icon = source_skiff.icon
WHEN NOT MATCHED THEN
  INSERT (icon, skiff_id)
    VALUES (source_skiff.icon,
      source_skiff.skiff_id);
""",
        "params": {"icon": icon, "skiff_id": skiff_id},
    }


def prune_skiff_dye_slots(skiff_id: int, slot_indices: list[int]) -> dict:
    return {
        "query": """
DELETE FROM gwapese.skiff_dye_slot
WHERE skiff_id = %(skiff_id)s::integer
  AND NOT slot_index = ANY (%(slot_indices)s::integer[]);
""",
        "params": {"skiff_id": skiff_id, "slot_indices": slot_indices},
    }


def upsert_skiff_dye_slots(
    color_id: int, material: str, skiff_id: int, slot_index: int
) -> dict:
    return {
        "query": """
MERGE INTO gwapese.skiff_dye_slot AS target_skiff_dye_slot
USING (
  VALUES (%(color_id)s::integer,
    %(material)s::text,
    %(skiff_id)s::integer,
    %(slot_index)s::integer)
) AS
  source_skiff_dye_slot (color_id, material, skiff_id, slot_index)
  ON target_skiff_dye_slot.skiff_id = source_skiff_dye_slot.skiff_id
  AND target_skiff_dye_slot.slot_index = source_skiff_dye_slot.slot_index
WHEN NOT MATCHED THEN
  INSERT (color_id, material, skiff_id, slot_index)
    VALUES (source_skiff_dye_slot.color_id,
      source_skiff_dye_slot.material,
      source_skiff_dye_slot.skiff_id,
      source_skiff_dye_slot.slot_index);
""",
        "params": {
            "color_id": color_id,
            "material": material,
            "skiff_id": skiff_id,
            "slot_index": slot_index,
        },
    }


def upsert_skiff_name(app_name: str, lang_tag: str, original: str, skiff_id: int):
    return {
        "query": """
MERGE INTO gwapese.skiff_name AS target_skiff_name
USING (
    VALUES (
        %(app_name)s::text,
        %(lang_tag)s::text,
        %(original)s::text,
        %(skiff_id)s::integer)
) AS
  source_skiff_name (app_name, lang_tag, original, skiff_id)
  ON target_skiff_name.app_name = source_skiff_name.app_name
  AND target_skiff_name.lang_tag = source_skiff_name.lang_tag
  AND target_skiff_name.skiff_id = source_skiff_name.skiff_id
WHEN MATCHED
  AND target_skiff_name.original != source_skiff_name.original THEN
  UPDATE SET
    original = source_skiff_name.original
WHEN NOT MATCHED THEN
  INSERT (app_name, lang_tag, original, skiff_id)
    VALUES (source_skiff_name.app_name,
      source_skiff_name.lang_tag,
      source_skiff_name.original,
      source_skiff_name.skiff_id);""",
        "params": {
            "app_name": app_name,
            "lang_tag": lang_tag,
            "original": original,
            "skiff_id": skiff_id,
        },
    }
