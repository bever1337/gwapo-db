-- Deploy gawpo-db:rarity to pg
BEGIN;

CREATE TABLE gwapese.rarities (
  rarity text NOT NULL,
  CONSTRAINT rarities_PK PRIMARY KEY (rarity)
);

INSERT INTO gwapese.rarities (rarity)
  VALUES ('Junk'),
  ('Basic'),
  ('Fine'),
  ('Masterwork'),
  ('Rare'),
  ('Exotic'),
  ('Ascended'),
  ('Legendary');

COMMIT;
