-- Deploy gawpo-db:race to pg
-- requires: schema
-- requires: history
BEGIN;

CREATE TABLE gwapese.race (
  race_name text NOT NULL,
  CONSTRAINT race_PK PRIMARY KEY (race_name)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'race');

CREATE TABLE gwapese.historical_race (
  LIKE gwapese.race
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'race', 'historical_race');

-- CREATE OR REPLACE PROCEDURE gwapese.upsert_race (in_race_name text)
--   AS $$
-- BEGIN
--   MERGE INTO gwapese.race AS target_race
--   USING (
--   VALUES (in_race_name)) AS source_race (race_name) ON target_race.race_name =
--     source_race.race_name
--   WHEN NOT MATCHED THEN
--     INSERT (race_name)
--       VALUES (in_race_name);
-- END;
-- $$
-- LANGUAGE plpgsql;
COMMIT;
