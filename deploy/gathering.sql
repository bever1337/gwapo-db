-- Deploy gawpo-db:gathering to pg
BEGIN;

CREATE TABLE gwapese.gathering_tools (
  tool text NOT NULL,
  CONSTRAINT gathering_tools_PK PRIMARY KEY (tool)
);

INSERT INTO gwapese.gathering_tools (tool)
  VALUES ('Fishing'),
  ('Foraging'),
  ('Logging'),
  ('Mining'),
  ('Bait'),
  ('Lure');

COMMIT;
