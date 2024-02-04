-- Verify gawpo-db:mount on pg
BEGIN;

SELECT
  mount_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mount
WHERE
  FALSE;

SELECT
  mount_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mount_history
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  mount_id,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mount_name
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  mount_id,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.mount_name_history
WHERE
  FALSE;

ROLLBACK;
