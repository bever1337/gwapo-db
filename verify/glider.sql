-- Verify gwapo-db:glider on pg
BEGIN;

SELECT
  glider_id,
  icon,
  presentation_order,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.glider
WHERE
  FALSE;

SELECT
  glider_id,
  icon,
  presentation_order,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.glider_history
WHERE
  FALSE;

SELECT
  app_name,
  glider_id,
  original,
  lang_tag,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.glider_description
WHERE
  FALSE;

SELECT
  app_name,
  glider_id,
  original,
  lang_tag,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.glider_description_history
WHERE
  FALSE;

SELECT
  color_id,
  glider_id,
  slot_index,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.glider_dye_slot
WHERE
  FALSE;

SELECT
  color_id,
  glider_id,
  slot_index,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.glider_dye_slot_history
WHERE
  FALSE;

SELECT
  app_name,
  glider_id,
  original,
  lang_tag,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.glider_name
WHERE
  FALSE;

SELECT
  app_name,
  glider_id,
  original,
  lang_tag,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.glider_name_history
WHERE
  FALSE;

ROLLBACK;
