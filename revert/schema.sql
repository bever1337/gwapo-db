-- Revert gwapo-db:schema from pg
BEGIN;

DROP SCHEMA IF EXISTS gwapese;

DROP EXTENSION IF EXISTS pg_trgm;

COMMIT;
