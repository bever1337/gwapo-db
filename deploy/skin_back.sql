-- Deploy gawpo-db:skin_back to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: races
-- requires: skin
BEGIN;

CREATE TABLE gwapese.skin_back (
  icon text NOT NULL,
  rarity text NOT NULL,
  skin_id smallint UNIQUE NOT NULL,
  skin_type text GENERATED ALWAYS AS ('Back') STORED,
  CONSTRAINT skin_back_pk PRIMARY KEY (skin_id, skin_type),
  CONSTRAINT skin_identifies_skin_back_fk FOREIGN KEY (skin_id) REFERENCES
    gwapese.skin (skin_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT skin_type_identifies_skin_back_fk FOREIGN KEY (skin_id, skin_type)
    REFERENCES gwapese.skin_type (skin_id, skin_type) ON DELETE CASCADE ON
    UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_back');

CREATE TABLE gwapese.historical_skin_back (
  LIKE gwapese.skin_back
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_back', 'historical_skin_back');

CREATE TABLE gwapese.skin_back_description (
  app_name text NOT NULL,
  original text NOT NULL,
  lang_tag text NOT NULL,
  skin_id smallint NOT NULL,
  CONSTRAINT skin_back_description_pk PRIMARY KEY (app_name, lang_tag, skin_id),
  CONSTRAINT operating_copy_precedes_skin_back_description_fk FOREIGN KEY
    (app_name, lang_tag, original) REFERENCES gwapese.operating_copy (app_name,
    lang_tag, original) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT skin_back_identifies_skin_back_description_fk FOREIGN KEY
    (skin_id) REFERENCES gwapese.skin_back (skin_id) ON DELETE CASCADE ON
    UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_back_description');

CREATE TABLE gwapese.historical_skin_back (
  LIKE gwapese.skin_back_description
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_back_description', 'historical_skin_back_description');

CREATE TABLE gwapese.skin_back_flag (
  flag text NOT NULL,
  skin_id smallint NOT NULL,
  CONSTRAINT skin_back_flag_pk PRIMARY KEY (skin_id, flag),
  CONSTRAINT skin_back_identifies_skin_back_flag_fk FOREIGN KEY (skin_id)
    REFERENCES gwapese.skin_back (skin_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_back_flag');

CREATE TABLE gwapese.historical_skin_back (
  LIKE gwapese.skin_back_flag
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_back_flag', 'historical_skin_back_flag');

CREATE TABLE gwapese.skin_back_name (
  app_name text NOT NULL,
  original text NOT NULL,
  lang_tag text NOT NULL,
  skin_id smallint NOT NULL,
  CONSTRAINT skin_back_name_pk PRIMARY KEY (app_name, lang_tag, skin_id),
  CONSTRAINT operating_copy_precedes_skin_back_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.operating_copy (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT skin_back_identifies_skin_back_name_fk FOREIGN KEY (skin_id)
    REFERENCES gwapese.skin_back (skin_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_back_name');

CREATE TABLE gwapese.historical_skin_back (
  LIKE gwapese.skin_back_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_back_name', 'historical_skin_back_name');

CREATE TABLE gwapese.skin_back_restriction (
  restriction text NOT NULL,
  skin_id smallint NOT NULL,
  CONSTRAINT skin_back_restriction_pk PRIMARY KEY (skin_id, restriction),
  CONSTRAINT skin_back_identifies_skin_back_restriction_fk FOREIGN KEY
    (skin_id) REFERENCES gwapese.skin_back (skin_id) ON DELETE CASCADE,
  CONSTRAINT race_enumerates_skin_back_restriction_fk FOREIGN KEY (restriction)
    REFERENCES gwapese.race (race_name) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'skin_back_restriction');

CREATE TABLE gwapese.historical_skin_back (
  LIKE gwapese.skin_back_restriction
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_back_restriction', 'historical_skin_back_restriction');

COMMIT;
