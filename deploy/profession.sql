-- Deploy gwapo-db:profession to pg
-- requires: schema
-- requires: history
-- requires: lang
BEGIN;

CREATE TABLE gwapese.profession (
  code integer NOT NULL,
  icon_big text NOT NULL,
  icon text NOT NULL,
  profession_id text NOT NULL,
  CONSTRAINT profession_pk PRIMARY KEY (profession_id)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'profession');

CREATE TABLE gwapese.profession_history (
  LIKE gwapese.profession
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'profession', 'profession_history');

CREATE TABLE gwapese.profession_name (
  app_name text NOT NULL,
  lang_tag text NOT NULL,
  original text NOT NULL,
  profession_id text NOT NULL,
  CONSTRAINT profession_name_pk PRIMARY KEY (app_name, lang_tag, profession_id),
  CONSTRAINT profession_identifies_profession_name_fk FOREIGN KEY
    (profession_id) REFERENCES gwapese.profession (profession_id) ON DELETE
    CASCADE ON UPDATE CASCADE,
  CONSTRAINT operating_copy_precedes_profession_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.operating_copy (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'profession_name');

CREATE TABLE gwapese.profession_name_history (
  LIKE gwapese.profession_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'profession_name', 'profession_name_history');

COMMIT;
