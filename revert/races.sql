-- Revert gawpo-db:races from pg
BEGIN;

DROP TABLE gwapese.historical_race;

DROP TABLE gwapese.race;

COMMIT;
