-- Deploy gwapo-db:finisher to pg
-- requires: schema
-- requires: history
BEGIN;

CREATE TABLE gwapese.finisher (
  finisher_id integer NOT NULL,
  icon text NOT NULL,
  presentation_order integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT finisher_pk PRIMARY KEY (finisher_id)
);

CREATE TABLE gwapese.finisher_history (
  LIKE gwapese.finisher
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'finisher', 'finisher_history');

COMMIT;
