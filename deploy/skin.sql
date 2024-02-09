-- Deploy gwapo-db:skins to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: race
-- requires: color
BEGIN;

CREATE TABLE gwapese.skin (
  icon text,
  rarity text NOT NULL,
  skin_id integer NOT NULL,
  CONSTRAINT skin_pk PRIMARY KEY (skin_id)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin');

CREATE TABLE gwapese.skin_history (
  LIKE gwapese.skin
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin', 'skin_history');

CREATE TABLE gwapese.skin_description (
  app_name text NOT NULL,
  lang_tag text NOT NULL,
  original text NOT NULL,
  skin_id integer NOT NULL,
  CONSTRAINT skin_description_pk PRIMARY KEY (app_name, lang_tag, skin_id),
  CONSTRAINT operating_copy_precedes_skin_description_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.operating_copy (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT skin_identifies_skin_description_fk FOREIGN KEY (skin_id)
    REFERENCES gwapese.skin (skin_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_description');

CREATE TABLE gwapese.skin_description_history (
  LIKE gwapese.skin_description
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_description', 'skin_description_history');

CREATE TABLE gwapese.skin_flag (
  flag text NOT NULL,
  skin_id integer NOT NULL,
  CONSTRAINT skin_flag_pk PRIMARY KEY (skin_id, flag),
  CONSTRAINT skin_identifies_skin_flag_fk FOREIGN KEY (skin_id) REFERENCES
    gwapese.skin (skin_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_flag');

CREATE TABLE gwapese.skin_flag_history (
  LIKE gwapese.skin_flag
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_flag', 'skin_flag_history');

CREATE TABLE gwapese.skin_name (
  app_name text NOT NULL,
  original text NOT NULL,
  lang_tag text NOT NULL,
  skin_id integer NOT NULL,
  CONSTRAINT skin_name_pk PRIMARY KEY (app_name, lang_tag, skin_id),
  CONSTRAINT operating_copy_precedes_skin_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.operating_copy (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT skin_identifies_skin_name_fk FOREIGN KEY (skin_id) REFERENCES
    gwapese.skin (skin_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_name');

CREATE TABLE gwapese.skin_name_history (
  LIKE gwapese.skin_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_name', 'skin_name_history');

CREATE TABLE gwapese.skin_restriction (
  restriction text NOT NULL,
  skin_id integer NOT NULL,
  CONSTRAINT skin_restriction_pk PRIMARY KEY (skin_id, restriction),
  CONSTRAINT skin_identifies_skin_restriction_fk FOREIGN KEY (skin_id)
    REFERENCES gwapese.skin (skin_id) ON DELETE CASCADE,
  CONSTRAINT race_enumerates_skin_restriction_fk FOREIGN KEY (restriction)
    REFERENCES gwapese.race (race_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_restriction');

CREATE TABLE gwapese.skin_restriction_history (
  LIKE gwapese.skin_restriction
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_restriction', 'skin_restriction_history');

CREATE TABLE gwapese.skin_type (
  skin_id integer UNIQUE NOT NULL,
  skin_type text NOT NULL,
  CONSTRAINT skin_type_pk PRIMARY KEY (skin_id, skin_type),
  CONSTRAINT skin_identifies_skin_type_fk FOREIGN KEY (skin_id) REFERENCES
    gwapese.skin (skin_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_type');

CREATE TABLE gwapese.skin_type_history (
  LIKE gwapese.skin_type
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_type', 'skin_type_history');

CREATE TABLE gwapese.skin_armor (
  skin_id integer UNIQUE NOT NULL,
  skin_type text GENERATED ALWAYS AS ('Armor') STORED NOT NULL,
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
  color_id integer NOT NULL,
  material text NOT NULL,
  skin_id integer NOT NULL,
  slot_index integer NOT NULL,
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

CREATE TABLE gwapese.skin_back (
  skin_id integer UNIQUE NOT NULL,
  skin_type text GENERATED ALWAYS AS ('Back') STORED NOT NULL,
  CONSTRAINT skin_back_pk PRIMARY KEY (skin_id, skin_type),
  CONSTRAINT skin_identifies_skin_back_fk FOREIGN KEY (skin_id) REFERENCES
    gwapese.skin (skin_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT skin_type_identifies_skin_back_fk FOREIGN KEY (skin_id, skin_type)
    REFERENCES gwapese.skin_type (skin_id, skin_type) ON DELETE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_back');

CREATE TABLE gwapese.skin_back_history (
  LIKE gwapese.skin_back
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_back', 'skin_back_history');

CREATE TABLE gwapese.skin_gathering (
  skin_id integer UNIQUE NOT NULL,
  skin_type text GENERATED ALWAYS AS ('Gathering') STORED NOT NULL,
  tool text NOT NULL,
  CONSTRAINT skin_gathering_pk PRIMARY KEY (skin_id, skin_type),
  CONSTRAINT skin_identifies_skin_gathering_fk FOREIGN KEY (skin_id) REFERENCES
    gwapese.skin (skin_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT skin_type_identifies_skin_gathering_fk FOREIGN KEY (skin_id,
    skin_type) REFERENCES gwapese.skin_type (skin_id, skin_type) ON DELETE
    CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_gathering');

CREATE TABLE gwapese.skin_gathering_history (
  LIKE gwapese.skin_gathering
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_gathering', 'skin_gathering_history');

CREATE TABLE gwapese.skin_weapon (
  damage_type text NOT NULL,
  skin_id integer UNIQUE NOT NULL,
  skin_type text GENERATED ALWAYS AS ('Weapon') STORED NOT NULL,
  weapon_type text NOT NULL,
  CONSTRAINT skin_weapon_pk PRIMARY KEY (skin_id, skin_type),
  CONSTRAINT skin_identifies_skin_weapon_fk FOREIGN KEY (skin_id) REFERENCES
    gwapese.skin (skin_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT skin_type_identifies_skin_weapon_fk FOREIGN KEY (skin_id,
    skin_type) REFERENCES gwapese.skin_type (skin_id, skin_type) ON DELETE
    CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_weapon');

CREATE TABLE gwapese.skin_weapon_history (
  LIKE gwapese.skin_weapon
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_weapon', 'skin_weapon_history');

COMMIT;
