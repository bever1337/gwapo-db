-- Deploy gwapo-db:race to pg
-- requires: schema
-- requires: history
BEGIN;

CREATE TABLE gwapese.race (
  race_id text NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT race_pk PRIMARY KEY (race_id)
);

CREATE TABLE gwapese.race_history (
  LIKE gwapese.race
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'race', 'race_history');

COMMIT;
