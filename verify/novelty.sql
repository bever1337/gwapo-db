-- Verify gwapo-db:novelty on pg
BEGIN;

SELECT
  icon,
  novelty_id,
  slot,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.novelty
WHERE
  FALSE;

SELECT
  icon,
  novelty_id,
  slot,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.novelty_history
WHERE
  FALSE;

ROLLBACK;
