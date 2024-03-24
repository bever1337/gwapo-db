-- Verify gwapo-db:color on pg
BEGIN;

SELECT
  color_id,
  hue,
  material,
  rarity,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.color
WHERE
  FALSE;

SELECT
  color_id,
  hue,
  material,
  rarity,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.color_history
WHERE
  FALSE;

SELECT
  blue,
  color_id,
  green,
  red,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.color_base
WHERE
  FALSE;

SELECT
  blue,
  color_id,
  green,
  red,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.color_base_history
WHERE
  FALSE;

SELECT
  color_id,
  material,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.color_sample
WHERE
  FALSE;

SELECT
  color_id,
  material,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.color_sample_history
WHERE
  FALSE;

SELECT
  brightness,
  color_id,
  contrast,
  material,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.color_sample_adjustment
WHERE
  FALSE;

SELECT
  brightness,
  color_id,
  contrast,
  material,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.color_sample_adjustment_history
WHERE
  FALSE;

SELECT
  color_id,
  hue,
  lightness,
  material,
  saturation,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.color_sample_shift
WHERE
  FALSE;

SELECT
  color_id,
  hue,
  lightness,
  material,
  saturation,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.color_sample_shift_history
WHERE
  FALSE;

SELECT
  blue,
  color_id,
  green,
  material,
  red,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.color_sample_reference
WHERE
  FALSE;

SELECT
  blue,
  color_id,
  green,
  material,
  red,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.color_sample_reference_history
WHERE
  FALSE;

SELECT
  blue,
  color_id,
  green,
  material,
  perceived_lightness,
  red,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.color_sample_reference_perception
WHERE
  FALSE;

SELECT
  blue,
  color_id,
  green,
  material,
  perceived_lightness,
  red,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.color_sample_reference_perception_history
WHERE
  FALSE;

SELECT
  has_function_privilege('gwapese.rgb_to_hex(smallint, smallint, smallint)', 'execute');

SELECT
  has_function_privilege('gwapese.srgb_to_lin(double precision)', 'execute');

SELECT
  has_function_privilege('gwapese.rgb_to_y(double precision, double precision, double precision)', 'execute');

SELECT
  has_function_privilege('gwapese.y_to_lstar(double precision)', 'execute');

SELECT
  has_function_privilege('gwapese.rgb_to_lightness(smallint, smallint, smallint)', 'execute');

ROLLBACK;
