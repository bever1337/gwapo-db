-- Verify gawpo-db:schema on pg
BEGIN;

SELECT
  pg_catalog.HAS_SCHEMA_PRIVILEGE('gwapese', 'usage');

ROLLBACK;
