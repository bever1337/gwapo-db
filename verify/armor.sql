-- Verify gawpo-db:armor on pg
BEGIN;

SELECT
  slot
FROM
  gwapese.armor_slots
WHERE
  FALSE;

SELECT
  weight_class
FROM
  gwapese.armor_weights
WHERE
  FALSE;

ROLLBACK;
