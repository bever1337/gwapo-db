-- Deploy gawpo-db:skins to pg
BEGIN;

CREATE TABLE gwapese.skin_flags (
  skin_flag text NOT NULL,
  CONSTRAINT skin_flags_PK PRIMARY KEY (skin_flag)
);

INSERT INTO gwapese.skin_flags (skin_flag)
  VALUES ('ShowInWardrobe'),
  ('NoCost'),
  ('HideIfLocked'),
  ('OverrideRarity');

CREATE TABLE gwapese.skin_types (
  skin_type text NOT NULL,
  CONSTRAINT skin_types_PK PRIMARY KEY (skin_type)
);

INSERT INTO gwapese.skin_types (skin_type)
  VALUES ('Armor'),
  ('Back'),
  ('Gathering'),
  ('Weapon');

CREATE TABLE gwapese.skins (
  id smallint UNIQUE NOT NULL,
  icon text,
  rarity text NOT NULL,
  skin_type text NOT NULL,
  CONSTRAINT skins_PK PRIMARY KEY (id, skin_type),
  CONSTRAINT skins_FK_rarity FOREIGN KEY (rarity) REFERENCES gwapese.rarities (rarity),
  CONSTRAINT skins_FK_skin_type FOREIGN KEY (skin_type) REFERENCES
    gwapese.skin_types (skin_type)
);

CREATE TABLE gwapese.armor_skins (
  id smallint NOT NULL UNIQUE,
  skin_type text NOT NULL,
  slot text NOT NULL,
  weight_class text NOT NULL,
  CONSTRAINT armor_skins_PK PRIMARY KEY (id),
  CONSTRAINT armor_skins_CK_skin_type CHECK (skin_type = 'Armor'),
  CONSTRAINT armor_skins_FK_skins FOREIGN KEY (id, skin_type) REFERENCES
    gwapese.skins (id, skin_type) ON DELETE CASCADE,
  CONSTRAINT armor_skins_FK_slot FOREIGN KEY (slot) REFERENCES gwapese.armor_slots (slot),
  CONSTRAINT armor_skins_FK_weight_class FOREIGN KEY (weight_class) REFERENCES
    gwapese.armor_weights (weight_class)
);

CREATE TABLE gwapese.back_skins (
  id smallint NOT NULL UNIQUE,
  skin_type text NOT NULL,
  CONSTRAINT back_skins_PK PRIMARY KEY (id),
  CONSTRAINT back_skins_CK_skin_type CHECK (skin_type = 'Back'),
  CONSTRAINT back_skins_FK_skins FOREIGN KEY (id, skin_type) REFERENCES
    gwapese.skins (id, skin_type) ON DELETE CASCADE
);

CREATE TABLE gwapese.described_skins (
  id smallint NOT NULL,
  language_tag text NOT NULL,
  skin_description text,
  CONSTRAINT described_skins_PK PRIMARY KEY (id, language_tag),
  CONSTRAINT described_skins_FK_id FOREIGN KEY (id) REFERENCES gwapese.skins
    (id) ON DELETE CASCADE,
  CONSTRAINT described_skins_FK_language_tag FOREIGN KEY (language_tag)
    REFERENCES gwapese.language_tags (language_tag)
);

CREATE TABLE gwapese.dyed_skin_slots (
  id smallint NOT NULL,
  color smallint,
  material text,
  slot_index smallint NOT NULL,
  CONSTRAINT dyed_skin_slots_PK PRIMARY KEY (id, slot_index),
  CONSTRAINT dyed_skin_slots_FK_armor_id FOREIGN KEY (id) REFERENCES
    gwapese.armor_skins (id) ON DELETE CASCADE,
  CONSTRAINT dyed_skin_slots_FK_color FOREIGN KEY (color) REFERENCES gwapese.colors (id),
  CONSTRAINT dyed_skin_slots_FK_material FOREIGN KEY (material) REFERENCES
    gwapese.dyed_materials (material),
  CONSTRAINT dyed_skin_slots_FK_skin_id FOREIGN KEY (id) REFERENCES
    gwapese.skins (id) ON DELETE CASCADE
);

CREATE TABLE gwapese.flagged_skins (
  id smallint NOT NULL,
  skin_flag text NOT NULL,
  CONSTRAINT flagged_skins_PK PRIMARY KEY (id, skin_flag),
  CONSTRAINT flagged_skins_FK_id FOREIGN KEY (id) REFERENCES gwapese.skins (id)
    ON DELETE CASCADE,
  CONSTRAINT flagged_skins_FK_skin_flag FOREIGN KEY (skin_flag) REFERENCES
    gwapese.skin_flags (skin_flag)
);

CREATE TABLE gwapese.gathering_skins (
  id smallint NOT NULL,
  skin_type text NOT NULL,
  tool text NOT NULL,
  CONSTRAINT gathering_skins_PK PRIMARY KEY (id),
  CONSTRAINT gathering_skins_CK_skin_type CHECK (skin_type = 'Gathering'),
  CONSTRAINT gathering_skins_FK_skins FOREIGN KEY (id, skin_type) REFERENCES
    gwapese.skins (id, skin_type) ON DELETE CASCADE,
  CONSTRAINT gathering_skins_FK_tool FOREIGN KEY (tool) REFERENCES
    gwapese.gathering_tools (tool)
);

CREATE TABLE gwapese.named_skins (
  id smallint NOT NULL,
  language_tag text NOT NULL,
  skin_name text NOT NULL,
  CONSTRAINT named_skins_PK PRIMARY KEY (id, language_tag),
  CONSTRAINT named_skins_FK_id FOREIGN KEY (id) REFERENCES gwapese.skins (id)
    ON DELETE CASCADE,
  CONSTRAINT named_skins_FK_language_tag FOREIGN KEY (language_tag) REFERENCES
    gwapese.language_tags (language_tag)
);

CREATE TABLE gwapese.restricted_skins (
  id smallint NOT NULL,
  restriction text,
  CONSTRAINT restricted_skins_PK PRIMARY KEY (id, restriction),
  CONSTRAINT restricted_skins_FK_id FOREIGN KEY (id) REFERENCES gwapese.skins
    (id) ON DELETE CASCADE,
  CONSTRAINT restricted_skins_FK_restriction FOREIGN KEY (restriction)
    REFERENCES gwapese.races (race)
);

CREATE TABLE gwapese.weapon_skins (
  id smallint NOT NULL,
  damage_type text NOT NULL,
  skin_type text NOT NULL,
  weapon_type text NOT NULL,
  CONSTRAINT weapon_skins_PK PRIMARY KEY (id),
  CONSTRAINT weapon_skins_CK_skin_type CHECK (skin_type = 'Weapon'),
  CONSTRAINT weapon_skins_FK_damage_type FOREIGN KEY (damage_type) REFERENCES
    gwapese.damage_types (damage_type),
  CONSTRAINT weapon_skins_FK_skins FOREIGN KEY (id, skin_type) REFERENCES
    gwapese.skins (id, skin_type) ON DELETE CASCADE,
  CONSTRAINT weapon_skins_FK_weapon_type FOREIGN KEY (weapon_type) REFERENCES
    gwapese.weapon_types (weapon_type)
);

CREATE OR REPLACE PROCEDURE gwapese.upsert_skin (in_id smallint, in_icon text,
  in_rarity text, in_skin_type text)
  AS $$
BEGIN
  MERGE INTO gwapese.skins AS target_skin
  USING (
  VALUES (in_id)) AS source_skin (id) ON target_skin.id = source_skin.id
  WHEN MATCHED THEN
    UPDATE SET
      (icon, rarity, skin_type) = (in_icon, in_rarity, in_skin_type)
  WHEN NOT MATCHED THEN
    INSERT (id, icon, rarity, skin_type)
      VALUES (in_id, in_icon, in_rarity, in_skin_type);
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE gwapese.upsert_armor_skin (in_id smallint, in_icon
  text, in_rarity text, in_slot text, in_weight_class text)
  AS $$
BEGIN
  CALL gwapese.upsert_skin (in_id, in_icon, in_rarity, 'Armor');
  MERGE INTO gwapese.armor_skins AS target_armor_skin
  USING (
  VALUES (in_id)) AS source_armor_skin (id) ON target_armor_skin.id = source_armor_skin.id
  WHEN MATCHED THEN
    UPDATE SET
      (slot, weight_class) = (in_slot, in_weight_class)
  WHEN NOT MATCHED THEN
    INSERT (id, skin_type, slot, weight_class)
      VALUES (in_id, 'Armor', in_slot, in_weight_class);
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE gwapese.upsert_back_skin (in_id smallint, in_icon
  text, in_rarity text)
  AS $$
BEGIN
  CALL gwapese.upsert_skin (in_id, in_icon, in_rarity, 'Back');
  MERGE INTO gwapese.back_skins AS target_back_skin
  USING (
  VALUES (in_id)) AS source_back_skin (id) ON target_back_skin.id = source_back_skin.id
  WHEN NOT MATCHED THEN
    INSERT (id, skin_type)
      VALUES (in_id, 'Back');
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE gwapese.upsert_described_skin (in_id smallint,
  in_language_tag text, in_skin_description text)
  AS $$
BEGIN
  MERGE INTO gwapese.described_skins AS target_skin
  USING (
  VALUES (in_id, in_language_tag)) AS source_skin (id, language_tag) ON
    target_skin.id = source_skin.id
    AND target_skin.language_tag = source_skin.language_tag
  WHEN MATCHED THEN
    UPDATE SET
      skin_description = in_skin_description
  WHEN NOT MATCHED THEN
    INSERT (id, language_tag, skin_description)
      VALUES (in_id, in_language_tag, in_skin_description);
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE gwapese.upsert_dyed_skin_slot (in_id smallint,
  in_color smallint, in_material text, in_slot_index smallint)
  AS $$
BEGIN
  MERGE INTO gwapese.dyed_skin_slots AS target_dyed_skin_slot
  USING (
  VALUES (in_id, in_slot_index)) AS source_dyed_skin_slot (id, slot_index) ON
    target_dyed_skin_slot.id = source_dyed_skin_slot.id
    AND target_dyed_skin_slot.slot_index = source_dyed_skin_slot.slot_index
  WHEN MATCHED THEN
    UPDATE SET
      (color, material) = (in_color, in_material)
  WHEN NOT MATCHED THEN
    INSERT (id, color, material, slot_index)
      VALUES (in_id, in_color, in_material, in_slot_index);
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE gwapese.upsert_gathering_skin (in_id smallint,
  in_icon text, in_rarity text, in_tool text)
  AS $$
BEGIN
  CALL gwapese.upsert_skin (in_id, in_icon, in_rarity, 'Gathering');
  MERGE INTO gwapese.gathering_skins AS target_gathering_skin
  USING (
  VALUES (in_id)) AS source_gathering_skin (id) ON target_gathering_skin.id =
    source_gathering_skin.id
  WHEN MATCHED THEN
    UPDATE SET
      tool = in_tool
  WHEN NOT MATCHED THEN
    INSERT (id, skin_type, tool)
      VALUES (in_id, 'Gathering', in_tool);
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE gwapese.upsert_named_skin (in_id smallint,
  in_language_tag text, in_skin_name text)
  AS $$
BEGIN
  MERGE INTO gwapese.named_skins AS target_skin
  USING (
  VALUES (in_id, in_language_tag)) AS source_skin (id, language_tag) ON
    target_skin.id = source_skin.id
    AND target_skin.language_tag = source_skin.language_tag
  WHEN MATCHED THEN
    UPDATE SET
      skin_name = in_skin_name
  WHEN NOT MATCHED THEN
    INSERT (id, language_tag, skin_name)
      VALUES (in_id, in_language_tag, in_skin_name);
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE gwapese.upsert_weapon_skin (in_id smallint,
  in_damage_type text, in_icon text, in_rarity text, in_weapon_type text)
  AS $$
BEGIN
  CALL gwapese.upsert_skin (in_id, in_icon, in_rarity, 'Weapon');
  MERGE INTO gwapese.weapon_skins AS target_weapon_skin
  USING (
  VALUES (in_id)) AS source_weapon_skin (id) ON target_weapon_skin.id =
    source_weapon_skin.id
  WHEN MATCHED THEN
    UPDATE SET
      (damage_type, weapon_type) = (in_damage_type, in_weapon_type)
  WHEN NOT MATCHED THEN
    INSERT (id, damage_type, skin_type, weapon_type)
      VALUES (in_id, in_damage_type, 'Weapon', in_weapon_type);
END;
$$
LANGUAGE plpgsql;

COMMIT;
