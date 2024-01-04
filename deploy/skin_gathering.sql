-- Deploy gawpo-db:skin_gathering to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: race
-- requires: skin
BEGIN;

CREATE TABLE gwapese.skin_gathering (
  icon text NOT NULL,
  rarity text NOT NULL,
  skin_id smallint UNIQUE NOT NULL,
  skin_type text GENERATED ALWAYS AS ('Gathering') STORED,
  tool text NOT NULL,
  CONSTRAINT skin_gathering_pk PRIMARY KEY (skin_id, skin_type),
  CONSTRAINT skin_identifies_skin_gathering_fk FOREIGN KEY (skin_id) REFERENCES
    gwapese.skin (skin_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT skin_type_identifies_skin_gathering_fk FOREIGN KEY (skin_id,
    skin_type) REFERENCES gwapese.skin_type (skin_id, skin_type) ON DELETE
    CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_gathering');

CREATE TABLE gwapese.historical_skin_gathering (
  LIKE gwapese.skin_gathering
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_gathering', 'historical_skin_gathering');

CREATE TABLE gwapese.skin_gathering_description (
  app_name text NOT NULL,
  original text NOT NULL,
  lang_tag text NOT NULL,
  skin_id smallint NOT NULL,
  CONSTRAINT skin_gathering_description_pk PRIMARY KEY (app_name, lang_tag, skin_id),
  CONSTRAINT operating_copy_precedes_skin_gathering_description_fk FOREIGN KEY
    (app_name, lang_tag, original) REFERENCES gwapese.operating_copy (app_name,
    lang_tag, original) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT skin_gathering_identifies_skin_gathering_description_fk FOREIGN
    KEY (skin_id) REFERENCES gwapese.skin_gathering (skin_id) ON DELETE CASCADE
    ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_gathering_description');

CREATE TABLE gwapese.historical_skin_gathering_description (
  LIKE gwapese.skin_gathering_description
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_gathering_description', 'historical_skin_gathering_description');

CREATE TABLE gwapese.skin_gathering_flag (
  flag text NOT NULL,
  skin_id smallint NOT NULL,
  CONSTRAINT skin_gathering_flag_pk PRIMARY KEY (skin_id, flag),
  CONSTRAINT skin_gathering_identifies_skin_gathering_flag_fk FOREIGN KEY
    (skin_id) REFERENCES gwapese.skin_gathering (skin_id) ON DELETE CASCADE ON
    UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_gathering_flag');

CREATE TABLE gwapese.historical_skin_gathering_flag (
  LIKE gwapese.skin_gathering_flag
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_gathering_flag', 'historical_skin_gathering_flag');

CREATE TABLE gwapese.skin_gathering_name (
  app_name text NOT NULL,
  original text NOT NULL,
  lang_tag text NOT NULL,
  skin_id smallint NOT NULL,
  CONSTRAINT skin_gathering_name_pk PRIMARY KEY (app_name, lang_tag, skin_id),
  CONSTRAINT operating_copy_precedes_skin_gathering_name_fk FOREIGN KEY
    (app_name, lang_tag, original) REFERENCES gwapese.operating_copy (app_name,
    lang_tag, original) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT skin_gathering_identifies_skin_gathering_name_fk FOREIGN KEY
    (skin_id) REFERENCES gwapese.skin_gathering (skin_id) ON DELETE CASCADE ON
    UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_gathering_name');

CREATE TABLE gwapese.historical_skin_gathering_name (
  LIKE gwapese.skin_gathering_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_gathering_name', 'historical_skin_gathering_name');

CREATE TABLE gwapese.skin_gathering_restriction (
  restriction text NOT NULL,
  skin_id smallint NOT NULL,
  CONSTRAINT skin_gathering_restriction_pk PRIMARY KEY (skin_id, restriction),
  CONSTRAINT skin_gathering_identifies_skin_gathering_restriction_fk FOREIGN
    KEY (skin_id) REFERENCES gwapese.skin_gathering (skin_id) ON DELETE
    CASCADE,
  CONSTRAINT race_enumerates_skin_gathering_restriction_fk FOREIGN KEY
    (restriction) REFERENCES gwapese.race (race_name) ON DELETE CASCADE ON
    UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_gathering_restriction');

CREATE TABLE gwapese.historical_skin_gathering_restriction (
  LIKE gwapese.skin_gathering_restriction
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_gathering_restriction', 'historical_skin_gathering_restriction');

COMMIT;
