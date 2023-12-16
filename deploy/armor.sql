-- Deploy gawpo-db:armor to pg
BEGIN;

CREATE TABLE gwapese.armor_slots (
  slot text NOT NULL,
  CONSTRAINT armor_slots_PK PRIMARY KEY (slot)
);

INSERT INTO gwapese.armor_slots (slot)
  VALUES ('Boots'),
  ('Coat'),
  ('Gloves'),
  ('Helm'),
  ('HelmAquatic'),
  ('Leggings'),
  ('Shoulders');

CREATE TABLE gwapese.armor_weights (
  weight_class text NOT NULL,
  CONSTRAINT armor_weights_PK PRIMARY KEY (weight_class)
);

INSERT INTO gwapese.armor_weights (weight_class)
  VALUES ('Heavy'),
  ('Medium'),
  ('Light'),
  ('Clothing');

COMMIT;
