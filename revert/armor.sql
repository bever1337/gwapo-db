-- Revert gawpo-db:armor from pg
BEGIN;

DROP TABLE gwapese.armor_slots;

DROP TABLE gwapese.armor_weights;

COMMIT;
