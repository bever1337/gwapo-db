-- Verify gwapo-db:mount_skin on pg
BEGIN;

SELECT
  icon,
  mount_id,
  mount_skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mount_skin
WHERE
  FALSE;

SELECT
  icon,
  mount_id,
  mount_skin_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mount_skin_history
WHERE
  FALSE;

SELECT
  mount_id,
  mount_skin_id
FROM
  gwapese.mount_skin_default
WHERE
  FALSE;

SELECT
  mount_id,
  mount_skin_id
FROM
  gwapese.mount_skin_default_history
WHERE
  FALSE;

SELECT
  color_id,
  material,
  mount_skin_id,
  slot_index,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mount_skin_dye_slot
WHERE
  FALSE;

SELECT
  color_id,
  material,
  mount_skin_id,
  slot_index,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mount_skin_dye_slot_history
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  mount_skin_id,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mount_skin_name
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  mount_skin_id,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mount_skin_name_history
WHERE
  FALSE;

ROLLBACK;
