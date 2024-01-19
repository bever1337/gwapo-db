-- Deploy gawpo-db:skin_armor to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: race
-- requires: color
-- requires: skin
BEGIN;

CREATE TABLE gwapese.skin_armor (
  skin_id smallint UNIQUE NOT NULL,
  skin_type text GENERATED ALWAYS AS ('Armor') STORED,
  slot text NOT NULL,
  weight_class text NOT NULL,
  CONSTRAINT skin_armor_pk PRIMARY KEY (skin_id, skin_type),
  CONSTRAINT skin_identifies_skin_armor_fk FOREIGN KEY (skin_id) REFERENCES
    gwapese.skin (skin_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT skin_type_identifies_skin_armor_fk FOREIGN KEY (skin_id,
    skin_type) REFERENCES gwapese.skin_type (skin_id, skin_type) ON DELETE
    CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_armor');

CREATE TABLE gwapese.skin_armor_history (
  LIKE gwapese.skin_armor
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_armor', 'skin_armor_history');

CREATE TABLE gwapese.skin_armor_dye_slot (
  color_id smallint NOT NULL,
  material text NOT NULL,
  skin_id smallint NOT NULL,
  slot_index smallint NOT NULL,
  CONSTRAINT skin_armor_dye_slot_pk PRIMARY KEY (skin_id, slot_index),
  CONSTRAINT skin_armor_contains_skin_armor_dye_slot_fk FOREIGN KEY (skin_id)
    REFERENCES gwapese.skin_armor (skin_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT color_sample_illustrates_skin_armor_dye_slot_fk FOREIGN KEY
    (color_id, material) REFERENCES gwapese.color_sample (color_id, material)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_armor_dye_slot');

CREATE TABLE gwapese.skin_armor_dye_slot_history (
  LIKE gwapese.skin_armor_dye_slot
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_armor_dye_slot', 'skin_armor_dye_slot_history');

COMMIT;
