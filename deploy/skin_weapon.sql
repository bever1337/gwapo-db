-- Deploy gawpo-db:skin_weapon to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: races
-- requires: skin
BEGIN;

CREATE TABLE gwapese.skin_weapon (
  icon text NOT NULL,
  rarity text NOT NULL,
  damage_type text NOT NULL,
  skin_id smallint UNIQUE NOT NULL,
  skin_type text GENERATED ALWAYS AS ('Weapon') STORED,
  weapon_type text NOT NULL,
  CONSTRAINT skin_weapon_pk PRIMARY KEY (skin_id, skin_type),
  CONSTRAINT skin_identifies_skin_weapon_fk FOREIGN KEY (skin_id) REFERENCES
    gwapese.skin (skin_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT skin_type_identifies_skin_weapon_fk FOREIGN KEY (skin_id,
    skin_type) REFERENCES gwapese.skin_type (skin_id, skin_type) ON DELETE
    CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_weapon');

CREATE TABLE gwapese.historical_skin_weapon (
  LIKE gwapese.skin_weapon
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_weapon', 'historical_skin_weapon');

CREATE TABLE gwapese.skin_weapon_description (
  app_name text NOT NULL,
  original text NOT NULL,
  lang_tag text NOT NULL,
  skin_id smallint NOT NULL,
  CONSTRAINT skin_weapon_description_pk PRIMARY KEY (app_name, lang_tag, skin_id),
  CONSTRAINT operating_copy_precedes_skin_weapon_description_fk FOREIGN KEY
    (app_name, lang_tag, original) REFERENCES gwapese.operating_copy (app_name,
    lang_tag, original) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT skin_weapon_identifies_skin_weapon_description_fk FOREIGN KEY
    (skin_id) REFERENCES gwapese.skin_weapon (skin_id) ON DELETE CASCADE ON
    UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_weapon_description');

CREATE TABLE gwapese.historical_skin_weapon_description (
  LIKE gwapese.skin_weapon_description
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_weapo_descriptionn', 'historical_skin_weapon_description');

CREATE TABLE gwapese.skin_weapon_flag (
  flag text NOT NULL,
  skin_id smallint NOT NULL,
  CONSTRAINT skin_weapon_flag_pk PRIMARY KEY (skin_id, flag),
  CONSTRAINT skin_weapon_identifies_skin_weapon_flag_fk FOREIGN KEY (skin_id)
    REFERENCES gwapese.skin_weapon (skin_id) ON DELETE CASCADE ON UPDATE
    CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_weapon_flag');

CREATE TABLE gwapese.historical_skin_weapon_flag (
  LIKE gwapese.skin_weapon_flag
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_weapon_flag', 'historical_skin_weapon_flag');

CREATE TABLE gwapese.skin_weapon_name (
  app_name text NOT NULL,
  original text NOT NULL,
  lang_tag text NOT NULL,
  skin_id smallint NOT NULL,
  CONSTRAINT skin_weapon_name_pk PRIMARY KEY (app_name, lang_tag, skin_id),
  CONSTRAINT operating_copy_precedes_skin_weapon_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.operating_copy (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT skin_weapon_identifies_skin_weapon_name_fk FOREIGN KEY (skin_id)
    REFERENCES gwapese.skin_weapon (skin_id) ON DELETE CASCADE ON UPDATE
    CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_weapon_name');

CREATE TABLE gwapese.historical_skin_weapon_name (
  LIKE gwapese.skin_weapon_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_weapon_name', 'historical_skin_weapon_name');

CREATE TABLE gwapese.skin_weapon_restriction (
  restriction text NOT NULL,
  skin_id smallint NOT NULL,
  CONSTRAINT skin_weapon_restriction_pk PRIMARY KEY (skin_id, restriction),
  CONSTRAINT skin_weapon_identifies_skin_weapon_restriction_fk FOREIGN KEY
    (skin_id) REFERENCES gwapese.skin_weapon (skin_id) ON DELETE CASCADE,
  CONSTRAINT race_enumerates_skin_weapon_restriction_fk FOREIGN KEY
    (restriction) REFERENCES gwapese.race (race_name) ON DELETE CASCADE ON
    UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_weapon_restriction');

CREATE TABLE gwapese.historical_skin_weapon_restriction (
  LIKE gwapese.skin_weapon_restriction
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_weapon_restriction', 'historical_skin_weapon_restriction');

COMMIT;
