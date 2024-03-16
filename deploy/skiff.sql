-- Deploy gwapo-db:skiff to pg
-- requires: schema
-- requires: history
-- requires: color
BEGIN;

CREATE TABLE gwapese.skiff (
  icon text NOT NULL,
  skiff_id integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT skiff_pk PRIMARY KEY (skiff_id)
);

CREATE TABLE gwapese.skiff_history (
  LIKE gwapese.skiff
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skiff', 'skiff_history');

CREATE TABLE gwapese.skiff_dye_slot (
  color_id integer NOT NULL,
  material text NOT NULL,
  skiff_id integer NOT NULL,
  slot_index integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT skiff_dye_slot_pk PRIMARY KEY (skiff_id, slot_index),
  CONSTRAINT skiff_contains_dye_slot_fk FOREIGN KEY (skiff_id) REFERENCES
    gwapese.skiff (skiff_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT color_sample_illustrates_skiff_dye_slot_fk FOREIGN KEY (color_id,
    material) REFERENCES gwapese.color_sample (color_id, material) ON DELETE
    RESTRICT ON UPDATE CASCADE
);

CREATE TABLE gwapese.skiff_dye_slot_history (
  LIKE gwapese.skiff_dye_slot
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skiff_dye_slot', 'skiff_dye_slot_history');

COMMIT;
