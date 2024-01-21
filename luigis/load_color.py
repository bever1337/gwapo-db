import datetime
import json
import luigi
from os import path

import common
import load_lang
import transform_color


class LoadColor(luigi.Task):
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
            "load_color",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        return transform_color.TransformColor(
            extract_datetime=self.extract_datetime, lang_tag=self.lang_tag
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
                for color in json_input:
                    color_id: int = color["id"]

                    color_categories = color["categories"]
                    color_hue = (color_categories[0:1] or [None])[0]
                    color_material = (color_categories[1:2] or [None])[0]
                    color_rarity = (color_categories[2:3] or [None])[0]
                    cursor.execute(
                        **upsert_color(
                            color_id=color_id,
                            hue=color_hue,
                            material=color_material,
                            rarity=color_rarity,
                        )
                    )

                    cursor.execute(
                        **load_lang.upsert_operating_copy(
                            app_name="gw2",
                            lang_tag=self.lang_tag.value,
                            original=color["name"],
                        )
                    )
                    cursor.execute(
                        **upsert_color_name(
                            app_name="gw2",
                            color_id=color_id,
                            lang_tag=self.lang_tag.value,
                            original=color["name"],
                        )
                    )

                    color_base: list[int] = color["base_rgb"]
                    cursor.execute(
                        **upsert_color_base(
                            blue=color_base[2],
                            color_id=color_id,
                            green=color_base[1],
                            red=color_base[0],
                        )
                    )

                    for material in ["cloth", "fur", "leather", "metal"]:
                        sample = color[material]
                        cursor.execute(
                            **upsert_color_sample(color_id=color_id, material=material)
                        )
                        cursor.execute(
                            **upsert_color_sample_adjustment(
                                brightness=sample["brightness"],
                                color_id=color_id,
                                contrast=sample["contrast"],
                                material=material,
                            )
                        )
                        cursor.execute(
                            **upsert_color_sample_shift(
                                color_id=color_id,
                                hue=sample["hue"],
                                lightness=sample["lightness"],
                                material=material,
                                saturation=sample["saturation"],
                            )
                        )
                        sample_rgb = sample["rgb"]
                        cursor.execute(
                            **upsert_color_sample_reference(
                                blue=sample_rgb[2],
                                color_id=color_id,
                                green=sample_rgb[1],
                                material=material,
                                red=sample_rgb[0],
                            )
                        )

                cursor.execute(query="COMMIT")
                connection.commit()
                with self.output().open("w") as w_output:
                    w_output.write("ok")

            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                raise exception_instance


def upsert_color(color_id: int, hue: str, material: str, rarity: str):
    return {
        "query": """
MERGE INTO gwapese.color AS target_color
USING (
  VALUES (%s::smallint, %s::text, %s::text, %s::text)) AS
    source_color (color_id, hue, material, rarity) ON
    target_color.color_id = source_color.color_id
  WHEN MATCHED AND target_color.hue != source_color.hue
    OR target_color.material != source_color.material
    OR target_color.rarity != source_color.rarity THEN
    UPDATE SET
      (hue, material, rarity) = (source_color.hue,
        source_color.material, source_color.rarity)
  WHEN NOT MATCHED THEN
    INSERT (color_id, hue, material, rarity)
      VALUES (source_color.color_id,
        source_color.hue,
        source_color.material,
        source_color.rarity);
""",
        "params": (color_id, hue, material, rarity),
    }


def upsert_color_name(app_name: str, color_id: int, lang_tag: str, original: str):
    return {
        "query": """
MERGE INTO gwapese.color_name AS target_color_name
USING (
VALUES (%s::text, %s::smallint, %s::text, %s::text)) AS
  source_color_name (app_name, color_id, lang_tag, original)
  ON target_color_name.app_name = source_color_name.app_name
  AND target_color_name.lang_tag = source_color_name.lang_tag
  AND target_color_name.color_id = source_color_name.color_id
WHEN MATCHED AND target_color_name.original !=
  source_color_name.original THEN
  UPDATE SET
    original = source_color_name.original
WHEN NOT MATCHED THEN
  INSERT (app_name, color_id, lang_tag, original)
    VALUES (source_color_name.app_name,
      source_color_name.color_id,
      source_color_name.lang_tag,
      source_color_name.original);
""",
        "params": (app_name, color_id, lang_tag, original),
    }


def upsert_color_base(blue: int, color_id: int, green: int, red: int) -> dict[str, str]:
    return {
        "query": """
MERGE INTO gwapese.color_base AS target_color_base
USING (
VALUES (%s::smallint, %s::smallint, %s::smallint, %s::smallint)) AS
  source_color_base (blue, color_id, green, red)
  ON target_color_base.color_id = source_color_base.color_id
WHEN MATCHED AND target_color_base.blue != source_color_base.blue
  OR target_color_base.green != source_color_base.green
  OR target_color_base.red != source_color_base.red THEN
  UPDATE SET
    (blue, green, red) = (source_color_base.blue,
    source_color_base.green, source_color_base.red)
WHEN NOT MATCHED THEN
  INSERT (blue, color_id, green, red)
    VALUES (source_color_base.blue, source_color_base.color_id,
    source_color_base.green, source_color_base.red);
""",
        "params": (blue, color_id, green, red),
    }


def upsert_color_sample(color_id: int, material: str) -> dict[str, str]:
    return {
        "query": """
MERGE INTO gwapese.color_sample AS target_color_sample
USING (
VALUES (%s::smallint, %s::text)) AS source_color_sample (color_id, material)
  ON target_color_sample.color_id = source_color_sample.color_id
  AND target_color_sample.material = source_color_sample.material
WHEN NOT MATCHED THEN
  INSERT (color_id, material)
    VALUES (source_color_sample.color_id, source_color_sample.material);
""",
        "params": (color_id, material),
    }


def upsert_color_sample_adjustment(
    brightness: int, color_id: int, contrast: float, material: str
) -> dict[str, str]:
    return {
        "query": """
MERGE INTO gwapese.color_sample_adjustment AS target_adjustment
USING (
VALUES (%s::smallint, %s::smallint, CAST(%s AS double precision),
  %s::text)) AS source_adjustment (brightness, color_id,
  contrast, material)
  ON target_adjustment.color_id = source_adjustment.color_id
  AND target_adjustment.material = source_adjustment.material
WHEN MATCHED AND target_adjustment.brightness != source_adjustment.brightness
  OR target_adjustment.contrast != source_adjustment.contrast THEN
  UPDATE SET
    (brightness, contrast) = (source_adjustment.brightness,
    source_adjustment.contrast)
WHEN NOT MATCHED THEN
  INSERT (brightness, color_id, contrast, material)
    VALUES (source_adjustment.brightness, source_adjustment.color_id,
    source_adjustment.contrast, source_adjustment.material);
""",
        "params": (brightness, color_id, contrast, material),
    }


def upsert_color_sample_shift(
    color_id: int, hue: int, lightness: float, material: str, saturation: float
) -> dict[str, str]:
    return {
        "query": """
MERGE INTO gwapese.color_sample_shift AS target_shift
USING (
VALUES (%s::smallint, %s::smallint, CAST(%s AS double precision),
  %s::text, CAST(%s AS double precision))) AS source_shift
  (color_id, hue, lightness, material, saturation)
  ON target_shift.color_id = source_shift.color_id
  AND target_shift.material = source_shift.material
WHEN MATCHED AND target_shift.hue != source_shift.hue
  OR target_shift.lightness != source_shift.lightness
  OR target_shift.saturation != source_shift.saturation THEN
  UPDATE SET
    (hue, lightness, saturation) =
      (source_shift.hue, source_shift.lightness, source_shift.saturation)
WHEN NOT MATCHED THEN
  INSERT (color_id, hue, lightness, material, saturation)
    VALUES (source_shift.color_id, source_shift.hue,
    source_shift.lightness, source_shift.material, source_shift.saturation);
""",
        "params": (color_id, hue, lightness, material, saturation),
    }


def upsert_color_sample_reference(
    blue: int, color_id: int, green: int, material: str, red: int
) -> dict[str, str]:
    return {
        "query": """
MERGE INTO gwapese.color_sample_reference AS target_reference
USING (
VALUES (%s::smallint, %s::smallint, %s::smallint, %s,
  %s::smallint)) AS source_reference (blue, color_id,
  green, material, red) ON
  target_reference.color_id = source_reference.color_id
  AND target_reference.material = source_reference.material
WHEN MATCHED AND target_reference.blue != source_reference.blue
  OR target_reference.green != source_reference.green
  OR target_reference.red != source_reference.red THEN
  UPDATE SET
    (blue, green, red) = (source_reference.blue,
    source_reference.green, source_reference.red)
WHEN NOT MATCHED THEN
  INSERT (blue, color_id, green, material, red)
    VALUES (source_reference.blue, source_reference.color_id,
    source_reference.green, source_reference.material, source_reference.red);
""",
        "params": (blue, color_id, green, material, red),
    }
