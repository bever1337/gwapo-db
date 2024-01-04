-- Verify gawpo-db:races on pg
BEGIN;

SELECT
  has_function_privilege('temporal_tables.alter_table_to_temporal(text, text)', 'execute');

SELECT
  has_function_privilege('temporal_tables.create_historicize_trigger(text, text, text)', 'execute');

SELECT
  has_function_privilege('temporal_tables.drop_historicize_fn(text, text, text)', 'execute');

ROLLBACK;
