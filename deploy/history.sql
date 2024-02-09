-- Deploy gwapo-db:history to pg
BEGIN;

CREATE SCHEMA temporal_tables;

CREATE OR REPLACE FUNCTION temporal_tables.fmt_trigger_fn_name (IN
  in_temporal_table_name text)
  RETURNS text
  AS $quote_fmt_trigger_fn_name$
BEGIN
  RETURN in_temporal_table_name || '_tt_fn';
END;
$quote_fmt_trigger_fn_name$
LANGUAGE plpgsql
IMMUTABLE;

COMMENT ON FUNCTION temporal_tables.fmt_trigger_fn_name (text) IS 'WARNING: Function name is unescaped, unquoted, and potentially longer than an OID.';

CREATE OR REPLACE FUNCTION temporal_tables.fmt_trigger_name (IN
  in_temporal_table_name text)
  RETURNS text
  AS $quote_fmt_trigger_name$
BEGIN
  RETURN in_temporal_table_name || '_tt_tr';
END;
$quote_fmt_trigger_name$
LANGUAGE plpgsql
IMMUTABLE;

COMMENT ON FUNCTION temporal_tables.fmt_trigger_name (text) IS 'WARNING: Function name is unescaped, unquoted, and potentially longer than an OID.';

CREATE OR REPLACE FUNCTION temporal_tables.fmt_alter_table_to_temporal (IN
  in_schema_name text, IN in_table_name text)
  RETURNS text
  AS $quote_fmt_alter_table_to_temporal$
BEGIN
  RETURN format('ALTER TABLE %1$I.%2$I
    ADD COLUMN sysrange_lower timestamp(3) NOT NULL,
    ADD COLUMN sysrange_upper timestamp(3) NOT NULL;', in_schema_name, in_table_name);
END;
$quote_fmt_alter_table_to_temporal$
LANGUAGE plpgsql
IMMUTABLE;

CREATE OR REPLACE FUNCTION temporal_tables.fmt_create_temporal_fn (IN
  in_schema_name text, IN in_temporal_table_name text, IN in_history_table_name
  text)
  RETURNS text
  AS $quote_fmt_create_temporal_fn$
BEGIN
  RETURN format('CREATE OR REPLACE FUNCTION %1$I.%2$I ()
    RETURNS TRIGGER
    AS $$
  BEGIN
    IF TG_WHEN != ''BEFORE'' OR TG_LEVEL != ''ROW'' THEN
      RAISE trigger_protocol_violated;
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
      RAISE trigger_protocol_violated;
    END IF;
  END;
  $$
  LANGUAGE plpgsql;', in_schema_name, temporal_tables.fmt_trigger_fn_name
    (in_temporal_table_name), in_history_table_name);
END;
$quote_fmt_create_temporal_fn$
LANGUAGE plpgsql
IMMUTABLE;

CREATE OR REPLACE FUNCTION temporal_tables.fmt_create_table_trigger (IN
  in_schema_name text, IN in_temporal_table_name text)
  RETURNS text
  AS $quote_fmt_create_table_trigger$
BEGIN
  RETURN format('CREATE OR REPLACE TRIGGER %1$I
    BEFORE DELETE OR INSERT OR UPDATE ON %2$I.%3$I
    FOR EACH ROW
    EXECUTE FUNCTION %2$I.%4$I ();', temporal_tables.fmt_trigger_name
      (in_temporal_table_name), in_schema_name, in_temporal_table_name,
      temporal_tables.fmt_trigger_fn_name (in_temporal_table_name));
END;
$quote_fmt_create_table_trigger$
LANGUAGE plpgsql
IMMUTABLE;

CREATE OR REPLACE FUNCTION temporal_tables.fmt_drop_table_trigger (IN
  in_schema_name text, IN in_temporal_table_name text)
  RETURNS text
  AS $quote_fmt_drop_table_trigger$
BEGIN
  RETURN format('DROP TRIGGER %1$I ON %2$I.%3$I;', temporal_tables.fmt_trigger_name
    (in_temporal_table_name), in_schema_name, in_temporal_table_name);
END;
$quote_fmt_drop_table_trigger$
LANGUAGE plpgsql
IMMUTABLE;

CREATE OR REPLACE FUNCTION temporal_tables.fmt_drop_trigger_fn (IN
  in_schema_name text, IN in_temporal_table_name text)
  RETURNS text
  AS $quote_fmt_drop_trigger_fn$
BEGIN
  RETURN format('DROP FUNCTION %1$I.%2$I;', in_schema_name,
    temporal_tables.fmt_trigger_fn_name (in_temporal_table_name));
END;
$quote_fmt_drop_trigger_fn$
LANGUAGE plpgsql
IMMUTABLE;

CREATE OR REPLACE PROCEDURE temporal_tables.alter_table_to_temporal (IN
  in_schema_name text, IN in_table_name text)
  AS $quote_alter_table_to_temporal$
BEGIN
  EXECUTE temporal_tables.fmt_alter_table_to_temporal (in_schema_name, in_table_name);
END;
$quote_alter_table_to_temporal$
LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE temporal_tables.create_historicize_trigger (IN
  in_schema_name text, IN in_temporal_table_name text, IN in_history_table_name
  text)
  AS $quote_create_historicize_trigger$
BEGIN
  IF octet_length(temporal_tables.fmt_trigger_fn_name (in_temporal_table_name)) > 63 THEN
    RAISE string_data_right_truncation;
  END IF;
  IF octet_length(temporal_tables.fmt_trigger_name (in_temporal_table_name)) > 63 THEN
    RAISE string_data_right_truncation;
  END IF;
  EXECUTE temporal_tables.fmt_create_temporal_fn (in_schema_name,
    in_temporal_table_name, in_history_table_name);
  EXECUTE temporal_tables.fmt_create_table_trigger (in_schema_name,
    in_temporal_table_name);
END;
$quote_create_historicize_trigger$
LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE temporal_tables.drop_historicize_fn (IN
  in_schema_name text, IN in_temporal_table_name text)
  AS $quote_drop_historicize_fn$
BEGIN
  EXECUTE temporal_tables.fmt_drop_table_trigger (in_schema_name, in_temporal_table_name);
  EXECUTE temporal_tables.fmt_drop_trigger_fn (in_schema_name, in_temporal_table_name);
END;
$quote_drop_historicize_fn$
LANGUAGE plpgsql;

COMMIT;
