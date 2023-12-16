-- Revert gawpo-db:races from pg
BEGIN;

DROP PROCEDURE gwapese.insert_race;

DROP TABLE gwapese.races;

COMMIT;
