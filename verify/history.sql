-- Verify gawpo-db:history on pg
BEGIN;

SELECT
  has_function_privilege('temporal_tables.fmt_trigger_fn_name(text)', 'execute');

SELECT
  has_function_privilege('temporal_tables.fmt_trigger_name(text)', 'execute');

SELECT
  has_function_privilege('temporal_tables.fmt_alter_table_to_temporal(text, text)', 'execute');

SELECT
  has_function_privilege('temporal_tables.fmt_create_temporal_fn(text, text)', 'execute');

SELECT
  has_function_privilege('temporal_tables.fmt_create_table_trigger(text, text, text)', 'execute');

SELECT
  has_function_privilege('temporal_tables.fmt_drop_table_trigger(text, text, text)', 'execute');

SELECT
  has_function_privilege('temporal_tables.fmt_drop_trigger_fn(text, text)', 'execute');

SELECT
  has_function_privilege('temporal_tables.alter_table_to_temporal(text, text)', 'execute');

SELECT
  has_function_privilege('temporal_tables.create_historicize_trigger(text, text, text)', 'execute');

SELECT
  has_function_privilege('temporal_tables.drop_historicize_fn(text, text, text)', 'execute');

ROLLBACK;
