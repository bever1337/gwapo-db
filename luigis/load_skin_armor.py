import datetime
import json
import luigi
from os import path

import common
import transform_skin_type


class LoadSkinArmor(luigi.Task):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)

    def output(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.txt".format(
            lang_tag=self.lang_tag.value,
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
        )
        target_path = path.join(
            self.output_dir,
            "load_skin_armor",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        return transform_skin_type.TransformSkinType(
            extract_datetime=self.extract_datetime,
            lang_tag=self.lang_tag,
            skin_type=common.SkinType.Armor,
        )

    def run(self):
        with (
            self.input().open("r") as r_input_file,
            common.get_conn() as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute(query="BEGIN")
            try:
                for skin_line in r_input_file:
                    skin = json.loads(skin_line)
                    skin_id = skin["id"]
                    skin_details: dict = skin["details"]

                    cursor.execute(
                        **upsert_skin_armor(
                            skin_id=skin_id,
                            slot=skin_details["type"],
                            weight_class=skin_details["weight_class"],
                        )
                    )

                    dye_slots: dict = skin_details.get("dye_slots", {})
                    default_dye_slots: list[dict] = dye_slots.get("default", [])
                    slot_indices = [index for index in range(len(default_dye_slots))]
                    cursor.execute(
                        **trim_skin_armor_dye_slots(
                            skin_id=skin_id, slot_indices=slot_indices
                        )
                    )
                    for i, dye_slot in enumerate(default_dye_slots):
                        if dye_slot == None:
                            # second pass removes holes
                            cursor.execute(
                                **prune_skin_armor_dye_slot(
                                    skin_id=skin_id, slot_index=i
                                )
                            )
                        else:
                            # second pass fills holes
                            cursor.execute(
                                **upsert_skin_armor_dye_slot(
                                    color_id=dye_slot["color_id"],
                                    material=dye_slot["material"],
                                    skin_id=skin_id,
                                    slot_index=i,
                                )
                            )

                cursor.execute(query="COMMIT")
                connection.commit()
                with self.output().open("w") as w_output:
                    w_output.write("ok")

            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                raise exception_instance


def upsert_skin_armor(skin_id: int, slot: str, weight_class: str) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.skin_armor AS target_skin_armor
USING (
  VALUES (%(skin_id)s::integer, %(slot)s::text, %(weight_class)s::text)
) AS source_skin_armor (skin_id, slot, weight_class)
ON
  target_skin_armor.skin_id = source_skin_armor.skin_id
WHEN MATCHED
  AND target_skin_armor.slot != source_skin_armor.slot
  OR target_skin_armor.weight_class != source_skin_armor.weight_class THEN
  UPDATE SET
    (slot, weight_class) = (source_skin_armor.slot,
    source_skin_armor.weight_class)
WHEN NOT MATCHED THEN
  INSERT (skin_id, slot, weight_class)
    VALUES (source_skin_armor.skin_id,
      source_skin_armor.slot,
      source_skin_armor.weight_class);
""",
        "params": {"skin_id": skin_id, "slot": slot, "weight_class": weight_class},
    }


def trim_skin_armor_dye_slots(skin_id: int, slot_indices: list[int]) -> dict:
    return {
        "query": """
DELETE FROM gwapese.skin_armor_dye_slot
WHERE gwapese.skin_armor_dye_slot.skin_id = %(skin_id)s::integer
  AND NOT gwapese.skin_armor_dye_slot.slot_index = ANY (%(slot_indices)s::integer[]);
""",
        "params": {"skin_id": skin_id, "slot_indices": slot_indices},
    }


def prune_skin_armor_dye_slot(skin_id: int, slot_index: int) -> dict[str]:
    return {
        "query": """
DELETE FROM gwapese.skin_armor_dye_slot
WHERE gwapese.skin_armor_dye_slot.skin_id = %(skin_id)s::integer
  AND gwapese.skin_armor_dye_slot.slot_index = %(slot_index)s::integer
""",
        "params": {
            "skin_id": skin_id,
            "slot_index": slot_index,
        },
    }


def upsert_skin_armor_dye_slot(
    color_id: int, material: str, skin_id: int, slot_index: int
) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.skin_armor_dye_slot AS target_dye_slot
USING (
  VALUES (%(color_id)s::integer, %(material)s::text, %(skin_id)s::integer, %(slot_index)s::integer)
) AS source_dye_slot (color_id, material, skin_id, slot_index)
ON
  target_dye_slot.skin_id = source_dye_slot.skin_id
  AND target_dye_slot.slot_index = source_dye_slot.slot_index
WHEN MATCHED
  AND target_dye_slot.color_id != source_dye_slot.color_id
  OR target_dye_slot.material != source_dye_slot.material THEN
  UPDATE SET
    (color_id, material) = (source_dye_slot.color_id, source_dye_slot.material)
WHEN NOT MATCHED THEN
  INSERT (color_id, material, skin_id, slot_index)
    VALUES (source_dye_slot.color_id,
      source_dye_slot.material,
      source_dye_slot.skin_id,
      source_dye_slot.slot_index);
""",
        "params": {
            "color_id": color_id,
            "material": material,
            "skin_id": skin_id,
            "slot_index": slot_index,
        },
    }
