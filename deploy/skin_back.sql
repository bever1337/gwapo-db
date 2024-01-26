-- Deploy gawpo-db:skin_back to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: race
-- requires: skin
BEGIN;

CREATE TABLE gwapese.skin_back (
  skin_id integer UNIQUE NOT NULL,
  skin_type text GENERATED ALWAYS AS ('Back') STORED,
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

COMMIT;
