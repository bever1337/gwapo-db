import datetime
import json
import luigi
from os import path

import common
import extract_batch
import load_lang


class LoadMountSkin(luigi.Task):
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
            "load_mount_skin",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.ndjson".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        return extract_batch.ExtractBatch(
            entity_schema="../schema/gw2/v2/mounts/skins/skin.json",
            extract_datetime=self.extract_datetime,
            extract_dir=path.join(self.output_dir, "extract_mount_skin_id"),
            id_schema="../schema/gw2/v2/mounts/skins/index.json",
            output_file=path.join(
                self.output_dir,
                "extract_mount_skin",
                target_filename,
            ),
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/mounts/skins",
        )


def run(self):
    with (
        self.input().open("r") as ro_input_file,
        common.get_conn() as connection,
        connection.cursor() as cursor,
    ):
        cursor.execute(query="BEGIN")
        try:
            for mount_skin_line in ro_input_file:
                mount_skin = json.loads(mount_skin_line)
                mount_skin_id = mount_skin["id"]
                cursor.execute(
                    **upsert_mount_skin(
                        icon=mount_skin["icon"],
                        mount_id=mount_skin["mount"],
                        mount_skin_id=mount_skin_id,
                    )
                )

                mount_skin_dye_slots: list[dict] = mount_skin["dye_slots"]
                slot_indices = [index for index in range(len(mount_skin_dye_slots))]
                cursor.execute(
                    **prune_mount_skin_dye_slots(
                        mount_skin_id=mount_skin_id, slot_indices=slot_indices
                    )
                )
                for slot_index, dye_slot in enumerate(mount_skin_dye_slots):
                    cursor.execute(
                        **upsert_mount_skin_dye_slots(
                            color_id=dye_slot["color_id"],
                            material=dye_slot["material"],
                            mount_skin_id=mount_skin_id,
                            slot_index=slot_index,
                        )
                    )

                mount_skin_name = mount_skin["name"]
                cursor.execute(
                    **load_lang.upsert_operating_copy(
                        app_name="gw2",
                        lang_tag=self.lang_tag.value,
                        original=mount_skin_name,
                    )
                )
                cursor.execute(
                    **upsert_mount_skin_name(
                        app_name="gw2",
                        mount_skin_id=mount_skin_id,
                        lang_tag=self.lang_tag.value,
                        original=mount_skin_name,
                    )
                )

            cursor.execute(query="COMMIT")
            connection.commit()
            with self.output().open("w") as w_output:
                w_output.write("ok")

        except Exception as exception_instance:
            cursor.execute(query="ROLLBACK")
            raise exception_instance


def upsert_mount_skin(icon: str, mount_id: str, mount_skin_id: int) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.mount_skin AS target_mount_skin
USING (
  VALUES (%(icon)s::text, %(mount_id)s::text, %(mount_skin_id)s::integer)
) AS source_mount_skin (icon, mount_id mount_skin_id)
ON
  target_mount_skin.mount_id = source_mount_skin.mount_id
  AND target_mount_skin.mount_skin_id = source_mount_skin.mount_skin_id
WHEN MATCHED
  AND target_mount_skin.icon != source_mount_skin.icon THEN
  UPDATE SET
    icon = source_mount_skin.icon
WHEN NOT MATCHED THEN
  INSERT (icon, mount_id, mount_skin_id)
    VALUES (source_mount_skin.icon,
      source_mount_skin.mount_id,  
      source_mount_skin.mount_skin_id);
""",
        "params": {"icon": icon, "mount_id": mount_id, "mount_skin_id": mount_skin_id},
    }


def prune_mount_skin_dye_slots(mount_skin_id: int, slot_indices: list[int]) -> dict:
    return {
        "query": """
DELETE FROM gwapese.mount_skin_dye_slot
WHERE mount_skin_id = %(mount_skin_id)s::integer
  AND NOT slot_index = ANY (%(slot_indices)s::integer[]);
""",
        "params": {"mount_skin_id": mount_skin_id, "slot_indices": slot_indices},
    }


def upsert_mount_skin_dye_slots(
    color_id: int, material: str, mount_skin_id: int, slot_index: int
) -> dict:
    return {
        "query": """
MERGE INTO gwapese.mount_skin_dye_slot AS target_mount_skin_dye_slot
USING (
  VALUES (%(color_id)s::integer,
    %(material)s::text,
    %(mount_skin_id)s::integer,
    %(slot_index)s::integer)
) AS
  source_mount_skin_dye_slot (color_id, material, mount_skin_id, slot_index)
  ON target_mount_skin_dye_slot.mount_skin_id = source_mount_skin_dye_slot.mount_skin_id
  AND target_mount_skin_dye_slot.slot_index = source_mount_skin_dye_slot.slot_index
WHEN NOT MATCHED THEN
  INSERT (color_id, material, mount_skin_id, slot_index)
    VALUES (source_mount_skin_dye_slot.color_id,
      source_mount_skin_dye_slot.material,
      source_mount_skin_dye_slot.mount_skin_id,
      source_mount_skin_dye_slot.slot_index);
""",
        "params": {
            "color_id": color_id,
            "material": material,
            "mount_skin_id": mount_skin_id,
            "slot_index": slot_index,
        },
    }


def upsert_mount_skin_name(
    app_name: str, lang_tag: str, original: str, mount_skin_id: int
):
    return {
        "query": """
MERGE INTO gwapese.mount_skin_name AS target_mount_skin_name
USING (
    VALUES (
        %(app_name)s::text,
        %(lang_tag)s::text,
        %(original)s::text,
        %(mount_skin_id)s::integer)
) AS
  source_mount_skin_name (app_name, lang_tag, original, mount_skin_id)
  ON target_mount_skin_name.app_name = source_mount_skin_name.app_name
  AND target_mount_skin_name.lang_tag = source_mount_skin_name.lang_tag
  AND target_mount_skin_name.mount_skin_id = source_mount_skin_name.mount_skin_id
WHEN MATCHED
  AND target_mount_skin_name.original != source_mount_skin_name.original THEN
  UPDATE SET
    original = source_mount_skin_name.original
WHEN NOT MATCHED THEN
  INSERT (app_name, lang_tag, original, mount_skin_id)
    VALUES (source_mount_skin_name.app_name,
      source_mount_skin_name.lang_tag,
      source_mount_skin_name.original,
      source_mount_skin_name.mount_skin_id);""",
        "params": {
            "app_name": app_name,
            "lang_tag": lang_tag,
            "original": original,
            "mount_skin_id": mount_skin_id,
        },
    }
