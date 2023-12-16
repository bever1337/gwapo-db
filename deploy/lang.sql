-- Deploy gawpo-db:lang to pg
BEGIN;

CREATE TABLE gwapese.language_tags (
  language_tag text NOT NULL,
  CONSTRAINT language_tags_PK PRIMARY KEY (language_tag)
);

INSERT INTO gwapese.language_tags (language_tag)
  VALUES ('en'),
  ('es'),
  ('de'),
  ('fr'),
  ('zh');

COMMIT;
