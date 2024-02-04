-- Deploy gawpo-db:mount to pg
-- requires: schema
-- requires: history
-- requires: lang
BEGIN;

CREATE TABLE gwapese.mount (
  mount_id text NOT NULL,
  CONSTRAINT mount_pk PRIMARY KEY (mount_id)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'mount');

CREATE TABLE gwapese.mount_history (
  LIKE gwapese.mount
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'mount', 'mount_history');

CREATE TABLE gwapese.mount_name (
  app_name text NOT NULL,
  lang_tag text NOT NULL,
  mount_id text NOT NULL,
  original text NOT NULL,
  CONSTRAINT mount_name_pk PRIMARY KEY (app_name, lang_tag, mount_id),
  CONSTRAINT mount_identifies_mount_name_fk FOREIGN KEY (mount_id) REFERENCES
    gwapese.mount (mount_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT operating_copy_precedes_mount_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.operating_copy (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'mount_name');

CREATE TABLE gwapese.mount_name_history (
  LIKE gwapese.mount_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'mount_name', 'mount_name_history');

COMMIT;
