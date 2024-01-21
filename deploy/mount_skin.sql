-- Deploy gawpo-db:mount_skin to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: mount
BEGIN;

CREATE TABLE gwapese.mount_skin (
  icon text NOT NULL,
  mount_id text NOT NULL,
  mount_skin_id smallint UNIQUE NOT NULL,
  CONSTRAINT mount_skin_pk PRIMARY KEY (mount_id, mount_skin_id),
  CONSTRAINT mount_identifies_mount_skin_fk FOREIGN KEY (mount_id) REFERENCES
    gwapese.mount (mount_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'mount_skin');

CREATE TABLE gwapese.mount_skin_history (
  LIKE gwapese.mount_skin
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'mount_skin', 'mount_skin_history');

CREATE TABLE gwapese.mount_skin_default (
  mount_id text UNIQUE NOT NULL,
  mount_skin_id smallint NOT NULL,
  CONSTRAINT mount_skin_default_pk PRIMARY KEY (mount_id, mount_skin_id),
  CONSTRAINT mount_identifies_mount_skin_default_fk FOREIGN KEY (mount_id)
    REFERENCES gwapese.mount (mount_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT mount_skin_identifies_mount_skin_default_fk FOREIGN KEY (mount_id,
    mount_skin_id) REFERENCES gwapese.mount_skin (mount_id, mount_skin_id) ON
    DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'mount_skin_default');

CREATE TABLE gwapese.mount_skin_default_history (
  LIKE gwapese.mount_skin_default
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'mount_skin_default', 'mount_skin_default_history');

CREATE TABLE gwapese.mount_skin_dye_slot (
  color_id smallint NOT NULL,
  material text NOT NULL,
  mount_skin_id smallint NOT NULL,
  slot_index smallint NOT NULL,
  CONSTRAINT mount_skin_dye_slot_pk PRIMARY KEY (mount_skin_id, slot_index),
  CONSTRAINT mount_skin_contains_mount_skin_dye_slot_fk FOREIGN KEY
    (mount_skin_id) REFERENCES gwapese.mount_skin (mount_skin_id) ON DELETE
    CASCADE ON UPDATE CASCADE,
  CONSTRAINT color_sample_illustrates_mount_skin_dye_slot_fk FOREIGN KEY
    (color_id, material) REFERENCES gwapese.color_sample (color_id, material)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'mount_skin_dye_slot');

CREATE TABLE gwapese.mount_skin_dye_slot_history (
  LIKE gwapese.mount_skin_dye_slot
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'mount_skin_dye_slot', 'mount_skin_dye_slot_history');

CREATE TABLE gwapese.mount_skin_name (
  app_name text NOT NULL,
  lang_tag text NOT NULL,
  mount_skin_id smallint NOT NULL,
  original text NOT NULL,
  CONSTRAINT mount_skin_name_pk PRIMARY KEY (app_name, lang_tag, mount_skin_id),
  CONSTRAINT mount_skin_identifies_mount_skin_name_fk FOREIGN KEY
    (mount_skin_id) REFERENCES gwapese.mount_skin (mount_skin_id) ON DELETE
    CASCADE ON UPDATE CASCADE,
  CONSTRAINT operating_copy_precedes_mount_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.operating_copy (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE RESTRICT
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'mount_skin_name');

CREATE TABLE gwapese.mount_skin_name_history (
  LIKE gwapese.mount_skin_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'mount_skin_name', 'mount_skin_name_history');

COMMIT;
