import datetime
import json
import luigi
from os import path

import common
import load_lang
import transform_glider


class LoadGlider(luigi.Task):
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
            "load_glider",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        return transform_glider.TransformGlider(
            extract_datetime=self.extract_datetime,
            lang_tag=self.lang_tag,
            output_dir=self.output_dir,
        )

    def run(self):
        with (
            self.input().open("r") as r_input_file,
            common.get_conn() as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute(query="BEGIN")
            try:
                for glider_line in r_input_file:
                    glider = json.loads(glider_line)
                    glider_id = glider["id"]
                    cursor.execute(
                        **upsert_glider(
                            glider_id=glider_id,
                            icon=glider["icon"],
                            presentation_order=glider["order"],
                        )
                    )

                    glider_description = glider["description"]
                    if glider_description != "":
                        cursor.execute(
                            **load_lang.upsert_operating_copy(
                                app_name="gw2",
                                lang_tag=self.lang_tag.value,
                                original=glider_description,
                            )
                        )
                        cursor.execute(
                            **upsert_glider_description(
                                app_name="gw2",
                                glider_id=glider_id,
                                lang_tag=self.lang_tag.value,
                                original=glider_description,
                            )
                        )

                    glider_dye_slots: list[int] = glider["default_dyes"]
                    slot_indices = [index for index in range(len(glider_dye_slots))]
                    cursor.execute(
                        **prune_glider_dye_slots(
                            glider_id=glider_id, slot_indices=slot_indices
                        )
                    )
                    for slot_index, color_id in enumerate(glider_dye_slots):
                        cursor.execute(
                            **upsert_glider_dye_slot(
                                color_id=color_id,
                                glider_id=glider_id,
                                slot_index=slot_index,
                            )
                        )

                    glider_name = glider["name"]
                    cursor.execute(
                        **load_lang.upsert_operating_copy(
                            app_name="gw2",
                            lang_tag=self.lang_tag.value,
                            original=glider_name,
                        )
                    )
                    cursor.execute(
                        **upsert_glider_name(
                            app_name="gw2",
                            glider_id=glider_id,
                            lang_tag=self.lang_tag.value,
                            original=glider_name,
                        )
                    )

                cursor.execute(query="COMMIT")
                connection.commit()
                with self.output().open("w") as w_output:
                    w_output.write("ok")

            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                raise exception_instance


def upsert_glider(glider_id: int, icon: str, presentation_order: str) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.glider AS target_glider
USING (
  VALUES (%(glider_id)s::integer, %(icon)s::text, %(presentation_order)s::integer)
) AS source_glider (glider_id, icon, presentation_order)
ON
  target_glider.glider_id = source_glider.glider_id
WHEN MATCHED
  AND target_glider.icon != source_glider.icon
  OR target_glider.presentation_order != source_glider.presentation_order THEN
  UPDATE SET
    (icon, presentation_order) =
      (source_glider.icon, source_glider.presentation_order)
WHEN NOT MATCHED THEN
  INSERT (glider_id, icon, presentation_order)
    VALUES (source_glider.glider_id,
      source_glider.icon,
      source_glider.presentation_order);
""",
        "params": {
            "glider_id": glider_id,
            "icon": icon,
            "presentation_order": presentation_order,
        },
    }


def upsert_glider_description(
    app_name: str, glider_id: int, lang_tag: str, original: str
):
    return {
        "query": """
MERGE INTO gwapese.glider_description AS target_glider_description
USING (
VALUES (%(app_name)s::text, %(glider_id)s::integer,
  %(lang_tag)s::text, %(original)s::text)
) AS
  source_glider_description (app_name, glider_id, lang_tag, original)
  ON target_glider_description.app_name = source_glider_description.app_name
  AND target_glider_description.lang_tag = source_glider_description.lang_tag
  AND target_glider_description.glider_id = source_glider_description.glider_id
WHEN MATCHED
  AND target_glider_description.original != source_glider_description.original THEN
  UPDATE SET
    original = source_glider_description.original
WHEN NOT MATCHED THEN
  INSERT (app_name, glider_id, lang_tag, original)
    VALUES (source_glider_description.app_name,
      source_glider_description.glider_id,
      source_glider_description.lang_tag,
      source_glider_description.original);""",
        "params": {
            "app_name": app_name,
            "glider_id": glider_id,
            "lang_tag": lang_tag,
            "original": original,
        },
    }


def prune_glider_dye_slots(glider_id: int, slot_indices: list[int]) -> dict:
    return {
        "query": """
DELETE FROM gwapese.glider_dye_slot
WHERE glider_id = %(glider_id)s::integer
  AND NOT slot_index = ANY (%(slot_indices)s::integer[]);
""",
        "params": {"glider_id": glider_id, "slot_indices": slot_indices},
    }


def upsert_glider_dye_slot(color_id: int, glider_id: int, slot_index: int) -> dict:
    return {
        "query": """
MERGE INTO gwapese.glider_dye_slot AS target_glider_dye_slot
USING (
  VALUES (%(color_id)s::integer, %(glider_id)s::integer, %(slot_index)s::integer)
) AS
  source_glider_dye_slot (color_id, glider_id, slot_index)
  ON target_glider_dye_slot.glider_id = source_glider_dye_slot.glider_id
  AND target_glider_dye_slot.slot_index = source_glider_dye_slot.slot_index
WHEN NOT MATCHED THEN
  INSERT (color_id, glider_id, slot_index)
    VALUES (source_glider_dye_slot.color_id, source_glider_dye_slot.glider_id,
      source_glider_dye_slot.slot_index);
""",
        "params": {
            "color_id": color_id,
            "glider_id": glider_id,
            "slot_index": slot_index,
        },
    }


def upsert_glider_name(app_name: str, glider_id: int, lang_tag: str, original: str):
    return {
        "query": """
MERGE INTO gwapese.glider_name AS target_glider_name
USING (
VALUES (%(app_name)s::text, %(glider_id)s::integer, %(lang_tag)s::text, %(original)s::text)) AS
  source_glider_name (app_name, glider_id, lang_tag, original)
  ON target_glider_name.app_name = source_glider_name.app_name
  AND target_glider_name.lang_tag = source_glider_name.lang_tag
  AND target_glider_name.glider_id = source_glider_name.glider_id
WHEN MATCHED
  AND target_glider_name.original != source_glider_name.original THEN
  UPDATE SET
    original = source_glider_name.original
WHEN NOT MATCHED THEN
  INSERT (app_name, glider_id, lang_tag, original)
    VALUES (source_glider_name.app_name,
      source_glider_name.glider_id,
      source_glider_name.lang_tag,
      source_glider_name.original);""",
        "params": {
            "app_name": app_name,
            "glider_id": glider_id,
            "lang_tag": lang_tag,
            "original": original,
        },
    }
