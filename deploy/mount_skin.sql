-- Deploy gwapo-db:mount_skin to pg
-- requires: schema
-- requires: history
-- requires: color
-- requires: mount
BEGIN;

CREATE TABLE gwapese.mount_skin (
  icon text NOT NULL,
  mount_id text NOT NULL,
  mount_skin_id integer UNIQUE NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT mount_skin_pk PRIMARY KEY (mount_id, mount_skin_id),
  CONSTRAINT mount_identifies_skin_fk FOREIGN KEY (mount_id) REFERENCES
    gwapese.mount (mount_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.mount_skin_history (
  LIKE gwapese.mount_skin
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'mount_skin', 'mount_skin_history');

CREATE TABLE gwapese.mount_skin_default (
  mount_id text NOT NULL,
  mount_skin_id integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT mount_skin_default_pk PRIMARY KEY (mount_id),
  CONSTRAINT mount_skin_identifies_default_fk FOREIGN KEY (mount_id,
    mount_skin_id) REFERENCES gwapese.mount_skin (mount_id, mount_skin_id) ON
    DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.mount_skin_default_history (
  LIKE gwapese.mount_skin_default
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'mount_skin_default', 'mount_skin_default_history');

CREATE TABLE gwapese.mount_skin_dye_slot (
  color_id integer NOT NULL,
  material text NOT NULL,
  mount_skin_id integer NOT NULL,
  slot_index integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT mount_skin_dye_slot_pk PRIMARY KEY (mount_skin_id, slot_index),
  CONSTRAINT mount_skin_contains_dye_slot_fk FOREIGN KEY (mount_skin_id)
    REFERENCES gwapese.mount_skin (mount_skin_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT color_sample_illustrates_mount_skin_dye_slot_fk FOREIGN KEY
    (color_id, material) REFERENCES gwapese.color_sample (color_id, material)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE gwapese.mount_skin_dye_slot_history (
  LIKE gwapese.mount_skin_dye_slot
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'mount_skin_dye_slot', 'mount_skin_dye_slot_history');

COMMIT;
