-- Deploy gwapo-db:profession to pg
-- requires: schema
-- requires: history
BEGIN;

CREATE TABLE gwapese.profession (
  code integer NOT NULL,
  icon_big text NOT NULL,
  icon text NOT NULL,
  profession_id text NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT profession_pk PRIMARY KEY (profession_id)
);

CREATE TABLE gwapese.profession_history (
  LIKE gwapese.profession
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'profession', 'profession_history');

COMMIT;
