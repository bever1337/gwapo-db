-- Verify gwapo-db:skiff on pg
BEGIN;

SELECT
  icon,
  skiff_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skiff
WHERE
  FALSE;

SELECT
  icon,
  skiff_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skiff_history
WHERE
  FALSE;

SELECT
  color_id,
  material,
  skiff_id,
  slot_index,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skiff_dye_slot
WHERE
  FALSE;

SELECT
  color_id,
  material,
  skiff_id,
  slot_index,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.skiff_dye_slot_history
WHERE
  FALSE;

ROLLBACK;
