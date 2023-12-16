-- Revert gawpo-db:gathering from pg
BEGIN;

DROP TABLE gwapese.gathering_tools;

COMMIT;
