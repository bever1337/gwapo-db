import luigi
from psycopg import sql

import color_transform_csv
import common
import lang_load
from tasks import config
from tasks import load_csv


class WrapColor(luigi.WrapperTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        args = {"lang_tag": self.lang_tag, "task_datetime": self.task_datetime}
        yield LoadCsvColorHue(**args)
        yield LoadCsvColorMaterial(**args)
        yield LoadCsvColorRarity(**args)
        yield LoadCsvColor(**args)
        yield LoadCsvColorName(**args)
        yield LoadCsvColorSample(**args)
        yield LoadCsvColorBase(**args)
        yield LoadCsvColorSampleAdjustment(**args)
        yield LoadCsvColorSampleShift(**args)
        yield LoadCsvColorSampleReference(**args)
        yield LoadCsvColorSampleReferencePerception(**args)


class WrapColorTranslate(luigi.WrapperTask):
    app_name = luigi.Parameter(default="gw2")
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)

    def requires(self):
        for lang_tag in common.LangTag:
            if lang_tag == self.original_lang_tag:
                continue
            yield LoadCsvColorNameTranslation(
                original_lang_tag=self.original_lang_tag,
                task_datetime=self.task_datetime,
                translation_lang_tag=lang_tag,
            )


class LoadCsvColorTask(load_csv.LoadCsvTask):
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "color"


class LoadCsvColorHue(LoadCsvColorTask):
    table = "color_hue"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.color_hue
USING (
  SELECT DISTINCT ON
    (hue) hue
  FROM
    tempo_color_hue) AS color_hue_source
  ON gwapese.color_hue.hue = color_hue_source.hue
WHEN NOT MATCHED THEN
  INSERT (hue)
    VALUES (color_hue_source.hue);
"""
    )

    def requires(self):
        return {
            self.table: color_transform_csv.TransformCsvColorHue(
                lang_tag=self.lang_tag
            ),
        }


class LoadCsvColorMaterial(LoadCsvColorTask):
    table = "color_material"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.color_material
USING (
  SELECT DISTINCT ON
    (material) material
  FROM
    tempo_color_material) AS color_material_source
  ON gwapese.color_material.material = color_material_source.material
WHEN NOT MATCHED THEN
  INSERT (material)
    VALUES (color_material_source.material);
"""
    )

    def requires(self):
        return {
            self.table: color_transform_csv.TransformCsvColorMaterial(
                lang_tag=self.lang_tag
            ),
        }


class LoadCsvColorRarity(LoadCsvColorTask):
    table = "color_rarity"

    postcopy_sql = sql.SQL(
        """
MERGE INTO gwapese.color_rarity
USING (
  SELECT DISTINCT ON
    (rarity) rarity
  FROM
    tempo_color_rarity) AS color_rarity_source
  ON gwapese.color_rarity.rarity = color_rarity_source.rarity
WHEN NOT MATCHED THEN
  INSERT (rarity)
    VALUES (color_rarity_source.rarity);
"""
    )

    def requires(self):
        return {
            self.table: color_transform_csv.TransformCsvColorRarity(
                lang_tag=self.lang_tag
            ),
        }


class LoadCsvColor(LoadCsvColorTask):
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
    (hue, material, rarity) = (NULLIF(source_color.hue, ''), NULLIF(source_color.material, ''), NULLIF(source_color.rarity, ''))
WHEN NOT MATCHED THEN
  INSERT (color_id, hue, material, rarity)
    VALUES (source_color.color_id, NULLIF(source_color.hue, ''), NULLIF(source_color.material, ''),
      NULLIF(source_color.rarity, ''));
"""
    )

    def requires(self):
        return {
            self.table: color_transform_csv.TransformCsvColor(lang_tag=self.lang_tag),
            "hue": LoadCsvColorHue(lang_tag=self.lang_tag),
            "material": LoadCsvColorMaterial(lang_tag=self.lang_tag),
            "rarity": LoadCsvColorRarity(lang_tag=self.lang_tag),
        }


class LoadCsvColorBase(LoadCsvColorTask):
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
            self.table: color_transform_csv.TransformCsvColorBase(
                lang_tag=self.lang_tag
            ),
            "color": LoadCsvColor(lang_tag=self.lang_tag),
        }


class LoadCsvColorName(lang_load.LangLoadCopySourceTask):
    id_attributes = [("color_id", sql.SQL("integer NOT NULL"))]
    table = "color_name"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "color"

    def requires(self):
        return {
            self.table: color_transform_csv.TransformCsvColorName(
                lang_tag=self.lang_tag
            ),
            "color": LoadCsvColor(lang_tag=self.lang_tag),
            "lang": lang_load.LangLoad(),
        }


class LoadCsvColorNameTranslation(lang_load.LangLoadCopyTargetTask):
    id_attributes = [("color_id", sql.SQL("integer NOT NULL"))]
    table = "color_name_context"
    task_datetime = luigi.DateSecondParameter(default=config.gconfig().task_datetime)
    task_namespace = "color"
    widget_table = "color_name"

    def requires(self):
        return {
            self.table: color_transform_csv.TransformCsvColorNameTranslation(
                app_name=self.app_name,
                original_lang_tag=self.original_lang_tag,
                translation_lang_tag=self.translation_lang_tag,
            ),
            "color": LoadCsvColorName(lang_tag=self.original_lang_tag),
        }


class LoadCsvColorSample(LoadCsvColorTask):
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
            self.table: color_transform_csv.TransformCsvColorSample(
                lang_tag=self.lang_tag
            ),
            "color": LoadCsvColor(lang_tag=self.lang_tag),
        }


class LoadCsvColorSampleAdjustment(LoadCsvColorTask):
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
            self.table: color_transform_csv.TransformCsvColorSampleAdjustment(
                lang_tag=self.lang_tag
            ),
            "color_sample": LoadCsvColorSample(lang_tag=self.lang_tag),
        }


class LoadCsvColorSampleShift(LoadCsvColorTask):
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
            self.table: color_transform_csv.TransformCsvColorSampleShift(
                lang_tag=self.lang_tag
            ),
            "color_sample": LoadCsvColorSample(lang_tag=self.lang_tag),
        }


class LoadCsvColorSampleReference(LoadCsvColorTask):
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
            self.table: color_transform_csv.TransformCsvColorSampleReference(
                lang_tag=self.lang_tag
            ),
            "color_sample": LoadCsvColorSample(lang_tag=self.lang_tag),
        }


class LoadCsvColorSampleReferencePerception(LoadCsvColorTask):
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
            self.table: color_transform_csv.TransformCsvColorSampleReference(
                lang_tag=self.lang_tag
            ),
            "color_sample_reference": LoadCsvColorSampleReference(
                lang_tag=self.lang_tag
            ),
        }
