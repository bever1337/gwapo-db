-- Deploy gwapo-db:skiff to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: color
BEGIN;

CREATE TABLE gwapese.skiff (
  icon text NOT NULL,
  skiff_id integer NOT NULL,
  CONSTRAINT skiff_pk PRIMARY KEY (skiff_id)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skiff');

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
  CONSTRAINT skiff_dye_slot_pk PRIMARY KEY (skiff_id, slot_index),
  CONSTRAINT skiff_contains_skiff_dye_slot_fk FOREIGN KEY (skiff_id) REFERENCES
    gwapese.skiff (skiff_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT color_sample_illustrates_skiff_dye_slot_fk FOREIGN KEY (color_id,
    material) REFERENCES gwapese.color_sample (color_id, material) ON DELETE
    RESTRICT ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skiff_dye_slot');

CREATE TABLE gwapese.skiff_dye_slot_history (
  LIKE gwapese.skiff_dye_slot
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skiff_dye_slot', 'skiff_dye_slot_history');

CREATE TABLE gwapese.skiff_name (
  app_name text NOT NULL,
  lang_tag text NOT NULL,
  original text NOT NULL,
  skiff_id integer NOT NULL,
  CONSTRAINT skiff_name_pk PRIMARY KEY (app_name, lang_tag, skiff_id),
  CONSTRAINT skiff_identifies_skiff_name_fk FOREIGN KEY (skiff_id) REFERENCES
    gwapese.skiff (skiff_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT operating_copy_precedes_skiff_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.operating_copy (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skiff_name');

CREATE TABLE gwapese.skiff_name_history (
  LIKE gwapese.skiff_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skiff_name', 'skiff_name_history');

COMMIT;
