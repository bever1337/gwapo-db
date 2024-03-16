-- Deploy gwapo-db:outfit to pg
-- requires: schema
-- requires: history
BEGIN;

CREATE TABLE gwapese.outfit (
  icon text NOT NULL,
  outfit_id integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT outfit_pk PRIMARY KEY (outfit_id)
);

CREATE TABLE gwapese.outfit_history (
  LIKE gwapese.outfit
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'outfit', 'outfit_history');

COMMIT;
