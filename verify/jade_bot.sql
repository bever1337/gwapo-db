-- Verify gwapo-db:jade_bot on pg
BEGIN;

SELECT
  jade_bot_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.jade_bot
WHERE
  FALSE;

SELECT
  jade_bot_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.jade_bot_history
WHERE
  FALSE;

SELECT
  app_name,
  jade_bot_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.jade_bot_description
WHERE
  FALSE;

SELECT
  app_name,
  jade_bot_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.jade_bot_description_history
WHERE
  FALSE;

SELECT
  app_name,
  jade_bot_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.jade_bot_name
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  jade_bot_id,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.jade_bot_name_history
WHERE
  FALSE;

-- SELECT
--   item_id,
--   jade_bot_id,
--   sysrange_lower,
--   sysrange_upper
-- FROM
--   gwapese.jade_bot_unlock
-- WHERE
--   FALSE;
-- SELECT
--   item_id,
--   jade_bot_id,
--   sysrange_lower,
--   sysrange_upper
-- FROM
--   gwapese.jade_bot_unlock_history
-- WHERE
--   FALSE;
ROLLBACK;
