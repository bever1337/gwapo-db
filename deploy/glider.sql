-- Deploy gwapo-db:glider to pg
-- requires: schema
-- requires: history
-- requires: color
BEGIN;

CREATE TABLE gwapese.glider (
  glider_id integer NOT NULL,
  icon text NOT NULL,
  presentation_order integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT glider_pk PRIMARY KEY (glider_id)
);

CREATE TABLE gwapese.glider_history (
  LIKE gwapese.glider
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'glider', 'glider_history');

CREATE TABLE gwapese.glider_dye_slot (
  color_id integer NOT NULL,
  glider_id integer NOT NULL,
  slot_index integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT glider_dye_slot_pk PRIMARY KEY (glider_id, slot_index),
  CONSTRAINT color_identifies_glider_dye_slot_fk FOREIGN KEY (color_id)
    REFERENCES gwapese.color (color_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT glider_identifies_dye_slot_fk FOREIGN KEY (glider_id) REFERENCES
    gwapese.glider (glider_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.glider_dye_slot_history (
  LIKE gwapese.glider_dye_slot
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'glider_dye_slot', 'glider_dye_slot_history');

COMMIT;
