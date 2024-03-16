-- Verify gwapo-db:history on pg
BEGIN;

SELECT
  has_function_privilege('temporal_tables.fmt_trigger_fn_name(text)', 'execute');

SELECT
  has_function_privilege('temporal_tables.fmt_trigger_name(text)', 'execute');

SELECT
  has_function_privilege('temporal_tables.fmt_create_temporal_fn(text, text, text)', 'execute');

SELECT
  has_function_privilege('temporal_tables.fmt_create_table_trigger(text, text)', 'execute');

SELECT
  has_function_privilege('temporal_tables.create_historicize_trigger(text, text, text)', 'execute');

ROLLBACK;
