-- Deploy gawpo-db:skin_armor to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: races
-- requires: skin
BEGIN;

CREATE TABLE gwapese.skin_armor (
  icon text NOT NULL,
  rarity text NOT NULL,
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

CREATE TABLE gwapese.historical_skin_armor (
  LIKE gwapese.skin_armor
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_armor', 'historical_skin_armor');

CREATE TABLE gwapese.skin_armor_description (
  app_name text NOT NULL,
  original text NOT NULL,
  lang_tag text NOT NULL,
  skin_id smallint NOT NULL,
  CONSTRAINT skin_armor_description_pk PRIMARY KEY (app_name, lang_tag, skin_id),
  CONSTRAINT operating_copy_precedes_skin_armor_description_fk FOREIGN KEY
    (app_name, lang_tag, original) REFERENCES gwapese.operating_copy (app_name,
    lang_tag, original) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT skin_armor_identifies_skin_armor_description_fk FOREIGN KEY
    (skin_id) REFERENCES gwapese.skin_armor (skin_id) ON DELETE CASCADE ON
    UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_armor_description');

CREATE TABLE gwapese.historical_skin_armor_description (
  LIKE gwapese.skin_armor_description
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_armor_description', 'skin_armor_description');

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

CREATE TABLE gwapese.historical_skin_armor_dye_slot (
  LIKE gwapese.skin_armor_dye_slot
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_armor_dye_slot', 'historical_skin_armor_dye_slot');

CREATE TABLE gwapese.skin_armor_flag (
  flag text NOT NULL,
  skin_id smallint NOT NULL,
  CONSTRAINT skin_armor_flag_pk PRIMARY KEY (skin_id, flag),
  CONSTRAINT skin_armor_identifies_skin_armor_flag_fk FOREIGN KEY (skin_id)
    REFERENCES gwapese.skin_armor (skin_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_armor_flag');

CREATE TABLE gwapese.historical_skin_armor_flag (
  LIKE gwapese.skin_armor_flag
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_armor_flag', 'historical_skin_armor_flag');

CREATE TABLE gwapese.skin_armor_name (
  app_name text NOT NULL,
  original text NOT NULL,
  lang_tag text NOT NULL,
  skin_id smallint NOT NULL,
  CONSTRAINT skin_armor_name_pk PRIMARY KEY (app_name, lang_tag, skin_id),
  CONSTRAINT operating_copy_precedes_skin_armor_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.operating_copy (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT skin_armor_identifies_skin_armor_name_fk FOREIGN KEY (skin_id)
    REFERENCES gwapese.skin_armor (skin_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_armor_name');

CREATE TABLE gwapese.historical_skin_armor_name (
  LIKE gwapese.skin_armor_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_armor_name', 'historical_skin_armor_name');

CREATE TABLE gwapese.skin_armor_restriction (
  restriction text NOT NULL,
  skin_id smallint NOT NULL,
  CONSTRAINT skin_armor_restriction_pk PRIMARY KEY (skin_id, restriction),
  CONSTRAINT skin_armor_identifies_skin_armor_restriction_fk FOREIGN KEY
    (skin_id) REFERENCES gwapese.skin_armor (skin_id) ON DELETE CASCADE,
  CONSTRAINT race_enumerates_skin_armor_restriction_fk FOREIGN KEY
    (restriction) REFERENCES gwapese.race (race_name) ON DELETE CASCADE ON
    UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_armor_restriction');

CREATE TABLE gwapese.historical_skin_armor_restriction (
  LIKE gwapese.skin_armor_restriction
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_armor_restriction', 'historical_skin_armor_restriction');

COMMIT;
