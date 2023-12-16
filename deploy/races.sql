-- Deploy gawpo-db:races to pg
BEGIN;

CREATE TABLE gwapese.races (
  race text NOT NULL,
  CONSTRAINT races_PK PRIMARY KEY (race)
);

CREATE OR REPLACE PROCEDURE gwapese.insert_race (in_race text)
  AS $$
BEGIN
  MERGE INTO gwapese.races AS target_race
  USING (
  VALUES (in_race)) AS source_race (race) ON target_race.race = source_race.race
  WHEN NOT MATCHED THEN
    INSERT (race)
      VALUES (in_race);
END;
$$
LANGUAGE plpgsql;

COMMIT;
