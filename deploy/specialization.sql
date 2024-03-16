-- Deploy gwapo-db:specialization to pg
-- requires: schema
-- requires: history
-- requires: profession
BEGIN;

CREATE TABLE gwapese.specialization (
  background text NOT NULL,
  elite boolean NOT NULL,
  icon text NOT NULL,
  profession_id text NOT NULL,
  specialization_id integer UNIQUE NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT specialization_pk PRIMARY KEY (profession_id, specialization_id),
  CONSTRAINT profession_identifies_specialization_fk FOREIGN KEY
    (profession_id) REFERENCES gwapese.profession (profession_id)
);

CREATE TABLE gwapese.specialization_history (
  LIKE gwapese.specialization
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'specialization', 'specialization_history');

COMMIT;
