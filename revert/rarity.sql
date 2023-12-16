-- Revert gawpo-db:rarity from pg
BEGIN;

DROP TABLE gwapese.rarities;

COMMIT;
