-- Deploy gwapo-db:mini to pg
-- requires: schema
-- requires: history
BEGIN;

CREATE TABLE gwapese.mini (
  icon text NOT NULL,
  mini_id integer NOT NULL,
  presentation_order integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT mini_pk PRIMARY KEY (mini_id)
);

CREATE TABLE gwapese.mini_history (
  LIKE gwapese.mini
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'mini', 'mini_history');

COMMIT;
