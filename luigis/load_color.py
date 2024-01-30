import datetime
import luigi
from os import path

import common
import load_csv
import transform_color


class LoadColorTask(load_csv.LoadCsvTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)
    table = luigi.EnumParameter(enum=transform_color.ColorTable)

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
            extract_datetime=self.extract_datetime,
            lang_tag=self.lang_tag,
            output_dir=self.output_dir,
            table=self.table,
        )


class LoadColor(LoadColorTask):
    table = transform_color.ColorTable.Color

    precopy_sql = """
CREATE TEMPORARY TABLE tempo_color (
  LIKE gwapese.color
) ON COMMIT DROP;
ALTER TABLE tempo_color
  DROP COLUMN sysrange_lower,
  DROP COLUMN sysrange_upper;"""

    copy_sql = """
COPY tempo_color FROM STDIN (FORMAT 'csv', HEADER);"""

    postcopy_sql = """
MERGE INTO gwapese.color AS target_color
USING tempo_color AS source_color
ON target_color.color_id = source_color.color_id
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
    """


class LoadColorName(LoadColorTask):
    table = transform_color.ColorTable.ColorName

    precopy_sql = """
CREATE TEMPORARY TABLE tempo_color_name (
  LIKE gwapese.color_name
) ON COMMIT DROP;
ALTER TABLE tempo_color_name
  DROP COLUMN sysrange_lower,
  DROP COLUMN sysrange_upper;"""

    copy_sql = """
COPY tempo_color_name FROM STDIN (FORMAT 'csv', HEADER);"""

    postcopy_sql = """
MERGE INTO gwapese.operating_copy AS target_operating_copy
USING tempo_color_name AS source_operating_copy
ON target_operating_copy.app_name = source_operating_copy.app_name
  AND target_operating_copy.lang_tag = source_operating_copy.lang_tag
  AND target_operating_copy.original = source_operating_copy.original
WHEN NOT MATCHED THEN
    INSERT (app_name, lang_tag, original)
      VALUES (source_operating_copy.app_name,
        source_operating_copy.lang_tag,
        source_operating_copy.original);
MERGE INTO gwapese.color_name AS target_color_name
USING tempo_color_name AS source_color_name
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
"""


class LoadColorBase(LoadColorTask):
    table = transform_color.ColorTable.ColorBase

    precopy_sql = """
CREATE TEMPORARY TABLE tempo_color_base (
  LIKE gwapese.color_base
) ON COMMIT DROP;
ALTER TABLE tempo_color_base
  DROP COLUMN sysrange_lower,
  DROP COLUMN sysrange_upper;"""

    copy_sql = """
COPY tempo_color_base FROM STDIN (FORMAT 'csv', HEADER);"""

    postcopy_sql = """
MERGE INTO gwapese.color_base AS target_color_base
USING tempo_color_base AS source_color_base
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
"""


class LoadColorSample(LoadColorTask):
    table = transform_color.ColorTable.ColorSample

    precopy_sql = """
CREATE TEMPORARY TABLE tempo_color_sample (
  LIKE gwapese.color_sample
) ON COMMIT DROP;
ALTER TABLE tempo_color_sample
  DROP COLUMN sysrange_lower,
  DROP COLUMN sysrange_upper;"""

    copy_sql = """
COPY tempo_color_sample FROM STDIN (FORMAT 'csv', HEADER);"""

    postcopy_sql = """
MERGE INTO gwapese.color_sample AS target_color_sample
USING tempo_color_sample AS source_color_sample
  ON target_color_sample.color_id = source_color_sample.color_id
  AND target_color_sample.material = source_color_sample.material
WHEN NOT MATCHED THEN
  INSERT (color_id, material)
    VALUES (source_color_sample.color_id, source_color_sample.material);
"""


class LoadColorSampleAdjustment(LoadColorTask):
    table = transform_color.ColorTable.ColorSampleAdjustment

    precopy_sql = """
CREATE TEMPORARY TABLE tempo_color_sample_adjustment (
  LIKE gwapese.color_sample_adjustment
) ON COMMIT DROP;
ALTER TABLE tempo_color_sample_adjustment
  DROP COLUMN sysrange_lower,
  DROP COLUMN sysrange_upper;"""

    copy_sql = """
COPY tempo_color_sample_adjustment FROM STDIN (FORMAT 'csv', HEADER);"""

    postcopy_sql = """
MERGE INTO gwapese.color_sample_adjustment AS target_adjustment
USING tempo_color_sample_adjustment AS source_adjustment
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
"""


class LoadColorSampleShift(LoadColorTask):
    table = transform_color.ColorTable.ColorSampleShift

    precopy_sql = """
CREATE TEMPORARY TABLE tempo_color_sample_shift (
  LIKE gwapese.color_sample_shift
) ON COMMIT DROP;
ALTER TABLE tempo_color_sample_shift
  DROP COLUMN sysrange_lower,
  DROP COLUMN sysrange_upper;"""

    copy_sql = """
COPY tempo_color_sample_shift FROM STDIN (FORMAT 'csv', HEADER);"""

    postcopy_sql = """
MERGE INTO gwapese.color_sample_shift AS target_shift
USING tempo_color_sample_shift AS source_shift
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
"""


class LoadColorSampleReference(LoadColorTask):
    table = transform_color.ColorTable.ColorSampleReference

    precopy_sql = """
CREATE TEMPORARY TABLE tempo_color_sample_reference (
  LIKE gwapese.color_sample_reference
) ON COMMIT DROP;
ALTER TABLE tempo_color_sample_reference
  DROP COLUMN sysrange_lower,
  DROP COLUMN sysrange_upper;"""

    copy_sql = """
COPY tempo_color_sample_reference FROM STDIN (FORMAT 'csv', HEADER);"""

    postcopy_sql = """
MERGE INTO gwapese.color_sample_reference AS target_reference
USING tempo_color_sample_reference AS source_reference
ON target_reference.color_id = source_reference.color_id
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
"""
