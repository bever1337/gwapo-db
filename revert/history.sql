-- Revert gawpo-db:history from pg
BEGIN;

DROP FUNCTION temporal_tables.fmt_trigger_fn_name;

DROP FUNCTION temporal_tables.fmt_trigger_name;

DROP FUNCTION temporal_tables.fmt_alter_table_to_temporal;

DROP FUNCTION temporal_tables.fmt_create_temporal_fn;

DROP FUNCTION temporal_tables.fmt_create_table_trigger;

DROP FUNCTION temporal_tables.fmt_drop_table_trigger;

DROP FUNCTION temporal_tables.fmt_drop_trigger_fn;

DROP PROCEDURE temporal_tables.alter_table_to_temporal;

DROP PROCEDURE temporal_tables.create_historicize_trigger;

DROP PROCEDURE temporal_tables.drop_historicize_fn;

DROP SCHEMA temporal_tables;

COMMIT;
