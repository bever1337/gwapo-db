-- Deploy gawpo-db:race to pg
-- requires: schema
-- requires: history
BEGIN;

CREATE TABLE gwapese.race (
  race_name text NOT NULL,
  CONSTRAINT race_pk PRIMARY KEY (race_name)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'race');

CREATE TABLE gwapese.race_history (
  LIKE gwapese.race
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'race', 'race_history');

COMMIT;
