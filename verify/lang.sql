-- Verify gawpo-db:lang on pg
BEGIN;

SELECT
  language_tag
FROM
  gwapese.language_tags
WHERE
  FALSE;

ROLLBACK;
