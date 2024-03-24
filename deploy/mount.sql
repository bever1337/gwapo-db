-- Deploy gwapo-db:mount to pg
-- requires: schema
-- requires: history
BEGIN;

CREATE TABLE gwapese.mount (
  mount_id text NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT mount_pk PRIMARY KEY (mount_id)
);

CREATE TABLE gwapese.mount_history (
  LIKE gwapese.mount
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'mount', 'mount_history');

COMMIT;
