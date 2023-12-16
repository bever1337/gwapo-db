-- Verify gawpo-db:rarity on pg
BEGIN;

SELECT
  rarity
FROM
  gwapese.rarities
WHERE
  FALSE;

ROLLBACK;
