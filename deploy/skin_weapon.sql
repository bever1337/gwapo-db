-- Deploy gawpo-db:skin_weapon to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: race
-- requires: skin
BEGIN;

CREATE TABLE gwapese.skin_weapon (
  damage_type text NOT NULL,
  skin_id smallint UNIQUE NOT NULL,
  skin_type text GENERATED ALWAYS AS ('Weapon') STORED,
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
