-- Deploy gawpo-db:weapons to pg
BEGIN;

CREATE TABLE gwapese.damage_types (
  damage_type text NOT NULL,
  CONSTRAINT damage_types_PK PRIMARY KEY (damage_type)
);

INSERT INTO gwapese.damage_types (damage_type)
  VALUES ('Choking'),
  ('Fire'),
  ('Ice'),
  ('Lightning'),
  ('Physical');

CREATE TABLE gwapese.weapon_types (
  weapon_type text NOT NULL,
  CONSTRAINT weapon_types_PK PRIMARY KEY (weapon_type)
);

INSERT INTO gwapese.weapon_types (weapon_type)
  VALUES ('Axe'),
  ('Dagger'),
  ('Mace'),
  ('Pistol'),
  ('Scepter'),
  ('Sword'),
  ('Focus'),
  ('Shield'),
  ('Torch'),
  ('Warhorn'),
  ('Greatsword'),
  ('Hammer'),
  ('Longbow'),
  ('Rifle'),
  ('Shortbow'),
  ('Staff'),
  ('Spear'),
  ('Speargun'),
  ('Trident'),
  ('LargeBundle'),
  ('SmallBundle'),
  ('Toy'),
  ('ToyTwoHanded');

COMMIT;
