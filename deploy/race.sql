-- Deploy gawpo-db:race to pg
-- requires: schema
-- requires: history
-- requires: lang
BEGIN;

CREATE TABLE gwapese.race (
  race_id text NOT NULL,
  CONSTRAINT race_pk PRIMARY KEY (race_id)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'race');

CREATE TABLE gwapese.race_history (
  LIKE gwapese.race
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'race', 'race_history');

CREATE TABLE gwapese.race_name (
  app_name text NOT NULL,
  lang_tag text NOT NULL,
  original text NOT NULL,
  race_id text NOT NULL,
  CONSTRAINT race_name_pk PRIMARY KEY (app_name, lang_tag, race_id),
  CONSTRAINT race_identifies_race_name_fk FOREIGN KEY (race_id) REFERENCES
    gwapese.race (race_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT operating_copy_precedes_currency_description_fk FOREIGN KEY
    (app_name, lang_tag, original) REFERENCES gwapese.operating_copy (app_name,
    lang_tag, original) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'race_name');

CREATE TABLE gwapese.race_name_history (
  LIKE gwapese.race_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'race_name', 'race_name_history');

COMMIT;
