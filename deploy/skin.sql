-- Deploy gawpo-db:skins to pg
-- requires: schema
-- requires: history
-- requires: lang
BEGIN;

CREATE TABLE gwapese.skin (
  skin_id smallint NOT NULL,
  CONSTRAINT skin_pk PRIMARY KEY (skin_id)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin');

CREATE TABLE gwapese.historical_skin (
  LIKE gwapese.skin
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin', 'historical_skin');

CREATE TABLE gwapese.skin_type (
  skin_id smallint UNIQUE NOT NULL,
  skin_type text NOT NULL,
  CONSTRAINT skin_type_pk PRIMARY KEY (skin_id, skin_type),
  CONSTRAINT skin_identifies_skin_type_fk FOREIGN KEY (skin_id) REFERENCES
    gwapese.skin (skin_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_type');

CREATE TABLE gwapese.historical_skin_type (
  LIKE gwapese.skin_type
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_type', 'historical_skin_type');

COMMIT;
