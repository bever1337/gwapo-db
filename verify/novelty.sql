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

SELECT
  app_name,
  lang_tag,
  novelty_id,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.novelty_description
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  novelty_id,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.novelty_description_history
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  novelty_id,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.novelty_name
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  novelty_id,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.novelty_name_history
WHERE
  FALSE;

-- SELECT
--   item_id,
--   novelty_id,
--   sysrange_lower,
--   sysrange_upper
-- FROM
--   gwapese.novelty_unlock
-- WHERE
--   FALSE;
-- SELECT
--   item_id,
--   novelty_id,
--   sysrange_lower,
--   sysrange_upper
-- FROM
--   gwapese.novelty_unlock_history
-- WHERE
--   FALSE;
ROLLBACK;
