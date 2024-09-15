-- Deploy gwapo-db:schema to pg
BEGIN;

CREATE SCHEMA IF NOT EXISTS gwapese;

CREATE EXTENSION IF NOT EXISTS pg_trgm;

COMMIT;
