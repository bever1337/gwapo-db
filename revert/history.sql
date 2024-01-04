-- Revert gawpo-db:history from pg
BEGIN;

DROP FUNCTION temporal_tables.alter_table_to_temporal;

DROP FUNCTION temporal_tables.create_historicize_trigger;

DROP FUNCTION temporal_tables.drop_historicize_fn;

DROP SCHEMA temporal_tables;

COMMIT;
