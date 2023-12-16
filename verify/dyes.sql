-- Verify gawpo-db:dyes on pg
BEGIN;

SELECT
  hue
FROM
  gwapese.color_hue_categories
WHERE
  FALSE;

SELECT
  material
FROM
  gwapese.color_material_categories
WHERE
  FALSE;

SELECT
  rarity
FROM
  gwapese.color_rarity_categories
WHERE
  FALSE;

SELECT
  material
FROM
  gwapese.dyed_materials
WHERE
  FALSE;

SELECT
  id,
  hue,
  material,
  rarity
FROM
  gwapese.colors
WHERE
  FALSE;

SELECT
  id,
  blue,
  green,
  material,
  red
FROM
  gwapese.detailed_colors
WHERE
  FALSE;

SELECT
  id,
  color_name,
  language_tag
FROM
  gwapese.named_colors
WHERE
  FALSE;

SELECT
  HAS_FUNCTION_PRIVILEGE('gwapese.upsert_color(smallint, text, text, text)', 'execute');

SELECT
  HAS_FUNCTION_PRIVILEGE('gwapese.upsert_detailed_color(smallint, smallint, smallint, double precision, smallint, smallint, double precision, text, smallint, double precision)', 'execute');

SELECT
  HAS_FUNCTION_PRIVILEGE('gwapese.upsert_named_color(smallint, text, text)', 'execute');

SELECT
  HAS_FUNCTION_PRIVILEGE('gwapese.rgb_to_hex(smallint, smallint, smallint)', 'execute');

SELECT
  HAS_FUNCTION_PRIVILEGE('gwapese.srgb_to_lin(double precision)', 'execute');

SELECT
  HAS_FUNCTION_PRIVILEGE('gwapese.rgb_to_y(double precision, double precision, double precision)', 'execute');

SELECT
  HAS_FUNCTION_PRIVILEGE('gwapese.y_to_lstar(double precision)', 'execute');

SELECT
  HAS_FUNCTION_PRIVILEGE('gwapese.rgb_to_lightness(smallint, smallint, smallint)', 'execute');

ROLLBACK;
