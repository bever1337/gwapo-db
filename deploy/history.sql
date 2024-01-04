-- Deploy gawpo-db:history to pg
BEGIN;

CREATE SCHEMA temporal_tables;

CREATE OR REPLACE PROCEDURE temporal_tables.alter_table_to_temporal (IN
  in_schema_name text, IN in_table_name text)
  AS $$
BEGIN
  EXECUTE format('ALTER TABLE %1$I.%2$I
    ADD COLUMN sysrange_lower timestamp(3) NOT NULL,
    ADD COLUMN sysrange_upper timestamp(3) NOT NULL;', in_schema_name, in_table_name);
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE temporal_tables.create_historicize_trigger (IN
  in_schema_name text, IN in_present_table_name text, IN
  in_historical_table_name text)
  AS $$
BEGIN
  -- [schema, trigger_fn, history_table]
  EXECUTE format('CREATE OR REPLACE FUNCTION %1$I.%2$I ()
    RETURNS TRIGGER
    AS $$
  BEGIN
    IF TG_WHEN != ''BEFORE'' OR TG_LEVEL != ''ROW'' THEN
      RAISE TRIGGER_PROTOCOL_VIOLATED;
    END IF;
    IF TG_OP = ''DELETE'' THEN
      OLD.sysrange_upper = current_timestamp(3);
      INSERT INTO %1$I.%3$I
        VALUES (OLD.*);
      RETURN OLD;
    ELSIF TG_OP = ''INSERT'' THEN
      NEW.sysrange_lower = current_timestamp(3);
      NEW.sysrange_upper = ''infinity'';
      RETURN NEW;
    ELSIF TG_OP = ''UPDATE'' THEN
      OLD.sysrange_upper = current_timestamp(3);
      NEW.sysrange_lower = OLD.sysrange_upper;
      NEW.sysrange_upper = ''infinity'';
      INSERT INTO %1$I.%3$I
        VALUES (OLD.*);
      RETURN NEW;
    ELSE
      RAISE TRIGGER_PROTOCOL_VIOLATED;
    END IF;
  END;
  $$
  LANGUAGE plpgsql;', in_schema_name, 'historicize_' || in_present_table_name ||
    '_fn', in_historical_table_name);
  -- [trigger_name, schema, temporal_table, trigger_fn]
  EXECUTE format('CREATE OR REPLACE TRIGGER %1$I
    BEFORE DELETE OR INSERT OR UPDATE ON %2$I.%3$I
    EXECUTE FUNCTION %2$I.%4$I ();', 'historicize_' ||
      in_present_table_name || '_tr', in_schema_name,
      in_present_table_name, 'historicize_' || in_present_table_name ||
      '_fn');
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE temporal_tables.drop_historicize_fn (IN
  in_schema_name text, IN in_present_table_name text, IN
  in_historical_table_name text)
  AS $$
BEGIN
  -- [trigger_name, schema, temporal_table]
  EXECUTE format('DROP TRIGGER %1$I ON %2$I.%3$I;', 'historicize_' || in_present_table_name ||
    '_tr', in_schema_name, in_present_table_name);
  -- [schema, trigger_fn]
  EXECUTE format('DROP FUNCTION %1$I.%2$I;', in_schema_name, 'historicize_' ||
    in_present_table_name || '_fn');
END;
$$
LANGUAGE plpgsql;

-- CREATE OR REPLACE FUNCTION temporal_tables.historicize ()
--   RETURNS TRIGGER
--   AS $$
-- BEGIN
--   IF TG_OP = 'DELETE' THEN
--     OLD.sysrange_upper = current_timestamp(3);
--     EXECUTE format('INSERT INTO %1$I.%2$I VALUES ($1.*);', TG_ARGV[0], TG_ARGV[1])
--     USING OLD;
--     RETURN OLD;
--   ELSIF TG_OP = 'INSERT' THEN
--     NEW.sysrange_lower = current_timestamp(3);
--     NEW.sysrange_upper = 'infinity';
--     RETURN NEW;
--   ELSIF TG_OP = 'UPDATE' THEN
--     OLD.sysrange_upper = current_timestamp(3);
--     NEW.sysrange_lower = OLD.sysrange_upper;
--     NEW.sysrange_upper = 'infinity';
--     EXECUTE format('INSERT INTO %1$I.%2$I VALUES ($1.*);', TG_ARGV[0], TG_ARGV[1])
--     USING OLD;
--     RETURN NEW;
--   ELSE
--     RAISE TRIGGER_PROTOCOL_VIOLATED 'function "historicize" must be fired for INSERT or UPDATE or DELETE';
--   END IF;
-- END;
-- $$
-- LANGUAGE plpgsql;
-- COMMENT ON FUNCTION temporal_tables.historicize IS '(schema_name text, historical_table_name text) => trigger';
COMMIT;
