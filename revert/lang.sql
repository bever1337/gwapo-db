-- Revert gawpo-db:lang from pg
BEGIN;

DROP TABLE gwapese.language_tags;

COMMIT;
