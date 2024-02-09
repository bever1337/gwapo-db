-- Verify gwapo-db:schema on pg
BEGIN;

SELECT
  pg_catalog.has_schema_privilege('gwapese', 'usage');

ROLLBACK;
