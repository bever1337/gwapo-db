import luigi
from psycopg import sql

import common
import load_csv
import load_lang
import transform_color


class WrapColor(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def requires(self):
        args = {"lang_tag": self.lang_tag}
        yield LoadColor(**args)
        yield LoadColorName(**args)
        yield LoadColorSample(**args)
        yield LoadColorBase(**args)
        yield LoadColorSampleAdjustment(**args)
        yield LoadColorSampleShift(**args)
        yield LoadColorSampleReference(**args)
        yield LoadColorSampleReferencePerception(**args)


class LoadColorTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)


class LoadColor(LoadColorTask):
    table = "color"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.color AS target_color
USING tempo_color AS source_color ON target_color.color_id = source_color.color_id
WHEN MATCHED
  AND target_color.hue != source_color.hue
  OR target_color.material != source_color.material
  OR target_color.rarity != source_color.rarity THEN
  UPDATE SET
    (hue, material, rarity) = (source_color.hue, source_color.material, source_color.rarity)
WHEN NOT MATCHED THEN
  INSERT (color_id, hue, material, rarity)
    VALUES (source_color.color_id, source_color.hue, source_color.material,
      source_color.rarity);
"""
    )

    def requires(self):
        return {self.table: transform_color.TransformColor(lang_tag=self.lang_tag)}


class LoadColorBase(LoadColorTask):
    table = "color_base"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.color_base AS target_color_base
USING tempo_color_base AS source_color_base ON target_color_base.color_id =
  source_color_base.color_id
WHEN MATCHED
  AND target_color_base.blue != source_color_base.blue
  OR target_color_base.green != source_color_base.green
  OR target_color_base.red != source_color_base.red THEN
  UPDATE SET
    (blue, green, red) = (source_color_base.blue, source_color_base.green,
      source_color_base.red)
WHEN NOT MATCHED THEN
  INSERT (blue, color_id, green, red)
    VALUES (source_color_base.blue, source_color_base.color_id,
      source_color_base.green, source_color_base.red);
"""
    )

    def requires(self):
        return {
            self.table: transform_color.TransformColorBase(lang_tag=self.lang_tag),
            "color": LoadColor(lang_tag=self.lang_tag),
        }


class LoadColorName(LoadColorTask):
    table = "color_name"

    postcopy_sql = sql.Composed(
        [
            load_lang.merge_into_operating_copy.format(
                table_name=sql.Identifier("tempo_color_name")
            ),
            load_lang.merge_into_placed_copy.format(
                table_name=sql.Identifier("color_name"),
                temp_table_name=sql.Identifier("tempo_color_name"),
                pk_name=sql.Identifier("color_id"),
            ),
        ]
    )

    def requires(self):
        return {
            self.table: transform_color.TransformColorName(lang_tag=self.lang_tag),
            "color": LoadColor(lang_tag=self.lang_tag),
            "lang": load_lang.LoadLang(),
        }


class LoadColorSample(LoadColorTask):
    table = "color_sample"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.color_sample AS target_color_sample
USING tempo_color_sample AS source_color_sample ON target_color_sample.color_id
  = source_color_sample.color_id
  AND target_color_sample.material = source_color_sample.material
WHEN NOT MATCHED THEN
  INSERT (color_id, material)
    VALUES (source_color_sample.color_id, source_color_sample.material);
"""
    )

    def requires(self):
        return {
            self.table: transform_color.TransformColorSample(lang_tag=self.lang_tag),
            "color": LoadColor(lang_tag=self.lang_tag),
        }


class LoadColorSampleAdjustment(LoadColorTask):
    table = "color_sample_adjustment"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.color_sample_adjustment AS target_adjustment
USING tempo_color_sample_adjustment AS source_adjustment ON
  target_adjustment.color_id = source_adjustment.color_id
  AND target_adjustment.material = source_adjustment.material
WHEN MATCHED
  AND target_adjustment.brightness != source_adjustment.brightness
  OR target_adjustment.contrast != source_adjustment.contrast THEN
  UPDATE SET
    (brightness, contrast) = (source_adjustment.brightness, source_adjustment.contrast)
WHEN NOT MATCHED THEN
  INSERT (brightness, color_id, contrast, material)
    VALUES (source_adjustment.brightness, source_adjustment.color_id,
      source_adjustment.contrast, source_adjustment.material);
"""
    )

    def requires(self):
        return {
            self.table: transform_color.TransformColorSampleAdjustment(
                lang_tag=self.lang_tag
            ),
            "color_sample": LoadColorSample(lang_tag=self.lang_tag),
        }


class LoadColorSampleShift(LoadColorTask):
    table = "color_sample_shift"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.color_sample_shift AS target_shift
USING tempo_color_sample_shift AS source_shift (color_id, hue, lightness,
  material, saturation) ON target_shift.color_id = source_shift.color_id
  AND target_shift.material = source_shift.material
WHEN MATCHED
  AND target_shift.hue != source_shift.hue
  OR target_shift.lightness != source_shift.lightness
  OR target_shift.saturation != source_shift.saturation THEN
  UPDATE SET
    (hue, lightness, saturation) = (source_shift.hue, source_shift.lightness,
      source_shift.saturation)
WHEN NOT MATCHED THEN
  INSERT (color_id, hue, lightness, material, saturation)
    VALUES (source_shift.color_id, source_shift.hue, source_shift.lightness,
      source_shift.material, source_shift.saturation);
"""
    )

    def requires(self):
        return {
            self.table: transform_color.TransformColorSampleShift(
                lang_tag=self.lang_tag
            ),
            "color_sample": LoadColorSample(lang_tag=self.lang_tag),
        }


class LoadColorSampleReference(LoadColorTask):
    table = "color_sample_reference"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.color_sample_reference AS target_reference
USING tempo_color_sample_reference AS source_reference ON
  target_reference.color_id = source_reference.color_id
  AND target_reference.material = source_reference.material
WHEN MATCHED
  AND target_reference.blue != source_reference.blue
  OR target_reference.green != source_reference.green
  OR target_reference.red != source_reference.red THEN
  UPDATE SET
    (blue, green, red) = (source_reference.blue, source_reference.green,
      source_reference.red)
WHEN NOT MATCHED THEN
  INSERT (blue, color_id, green, material, red)
    VALUES (source_reference.blue, source_reference.color_id,
      source_reference.green, source_reference.material, source_reference.red);
"""
    )

    def requires(self):
        return {
            self.table: transform_color.TransformColorSampleReference(
                lang_tag=self.lang_tag
            ),
            "color_sample": LoadColorSample(lang_tag=self.lang_tag),
        }


class LoadColorSampleReferencePerception(LoadColorTask):
    table = "color_sample_reference_perception"

    precopy_sql = sql.Composed(
        [
            sql.SQL(
                """
CREATE TEMPORARY TABLE tempo_color_sample_reference_perception (
  LIKE gwapese.color_sample_reference_perception
) ON COMMIT DROP;
"""
            ),
            sql.SQL(
                """
ALTER TABLE tempo_color_sample_reference_perception
  DROP COLUMN perceived_lightness,
  DROP COLUMN IF EXISTS sysrange_lower,
  DROP COLUMN IF EXISTS sysrange_upper;
"""
            ),
        ]
    )

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.color_sample_reference_perception AS target_reference
USING tempo_color_sample_reference_perception AS source_reference ON
  target_reference.color_id = source_reference.color_id
  AND target_reference.material = source_reference.material
WHEN MATCHED
  AND target_reference.blue != source_reference.blue
  OR target_reference.green != source_reference.green
  OR target_reference.red != source_reference.red THEN
  UPDATE SET
    (blue, green, red) = (source_reference.blue, source_reference.green,
      source_reference.red)
WHEN NOT MATCHED THEN
  INSERT (blue, color_id, green, material, red)
    VALUES (source_reference.blue, source_reference.color_id,
      source_reference.green, source_reference.material, source_reference.red);
"""
    )

    def requires(self):
        return {
            self.table: transform_color.TransformColorSampleReference(
                lang_tag=self.lang_tag
            ),
            "color_sample_reference": LoadColorSampleReference(lang_tag=self.lang_tag),
        }
