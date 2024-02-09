-- Verify gwapo-db:finisher on pg
BEGIN;

SELECT
  finisher_id,
  icon,
  presentation_order,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.finisher
WHERE
  FALSE;

SELECT
  finisher_id,
  icon,
  presentation_order,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.finisher_history
WHERE
  FALSE;

SELECT
  app_name,
  finisher_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.finisher_detail
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  finisher_id,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.finisher_detail_history
WHERE
  FALSE;

SELECT
  app_name,
  finisher_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.finisher_name
WHERE
  FALSE;

SELECT
  app_name,
  lang_tag,
  finisher_id,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.finisher_name_history
WHERE
  FALSE;

ROLLBACK;
