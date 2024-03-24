-- Verify gwapo-db:mount on pg
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

ROLLBACK;
