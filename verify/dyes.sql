-- Verify gawpo-db:color on pg
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
  gwapese.historical_color
WHERE
  FALSE;

SELECT
  app_name,
  color_id,
  original,
  lang_tag,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.color_name
WHERE
  FALSE;

SELECT
  app_name,
  color_id,
  original,
  lang_tag,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_color_name
WHERE
  FALSE;

SELECT
  blue,
  brightness,
  color_id,
  contrast,
  green,
  hue,
  lightness,
  material,
  perceived_lightness,
  red,
  rgb,
  saturation,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.color_sample
WHERE
  FALSE;

SELECT
  blue,
  brightness,
  color_id,
  contrast,
  green,
  hue,
  lightness,
  material,
  perceived_lightness,
  red,
  rgb,
  saturation,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.historical_color_sample
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
