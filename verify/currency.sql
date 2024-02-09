-- Verify gwapo-db:currency on pg
BEGIN;

SELECT
  currency_id,
  deprecated,
  icon,
  presentation_order,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.currency
WHERE
  FALSE;

SELECT
  currency_id,
  deprecated,
  icon,
  presentation_order,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.currency_history
WHERE
  FALSE;

SELECT
  category,
  currency_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.currency_category
WHERE
  FALSE;

SELECT
  category,
  currency_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.currency_category_history
WHERE
  FALSE;

SELECT
  app_name,
  currency_id,
  original,
  lang_tag,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.currency_description
WHERE
  FALSE;

SELECT
  app_name,
  currency_id,
  original,
  lang_tag,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.currency_description_history
WHERE
  FALSE;

SELECT
  app_name,
  currency_id,
  original,
  lang_tag,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.currency_name
WHERE
  FALSE;

SELECT
  app_name,
  currency_id,
  original,
  lang_tag,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.currency_name_history
WHERE
  FALSE;

ROLLBACK;
