-- Deploy gwapo-db:novelty to pg
-- requires: schema
-- requires: history
BEGIN;

CREATE TABLE gwapese.novelty (
  icon text NOT NULL,
  novelty_id integer NOT NULL,
  slot text NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT novelty_pk PRIMARY KEY (novelty_id)
);

CREATE TABLE gwapese.novelty_history (
  LIKE gwapese.novelty
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'novelty', 'novelty_history');

COMMIT;
