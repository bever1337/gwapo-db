-- Deploy gawpo-db:specialization to pg
-- requires: schema
-- requires: history
-- requires: lang
-- requires: profession
BEGIN;

CREATE TABLE gwapese.specialization (
  background text NOT NULL,
  elite boolean NOT NULL,
  icon text NOT NULL,
  profession_id text NOT NULL,
  specialization_id integer UNIQUE NOT NULL,
  CONSTRAINT specialization_pk PRIMARY KEY (profession_id, specialization_id),
  CONSTRAINT specialization_ak UNIQUE (specialization_id),
  CONSTRAINT profession_identifies_specialization_fk FOREIGN KEY
    (profession_id) REFERENCES gwapese.profession (profession_id)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'specialization');

CREATE TABLE gwapese.specialization_history (
  LIKE gwapese.specialization
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'specialization', 'specialization_history');

CREATE TABLE gwapese.specialization_name (
  app_name text NOT NULL,
  lang_tag text NOT NULL,
  original text NOT NULL,
  specialization_id integer NOT NULL,
  CONSTRAINT specialization_name_pk PRIMARY KEY (app_name, lang_tag, specialization_id),
  CONSTRAINT specialization_identifies_specialization_name_fk FOREIGN KEY
    (specialization_id) REFERENCES gwapese.specialization (specialization_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT operating_copy_precedes_specialization_name_fk FOREIGN KEY
    (app_name, lang_tag, original) REFERENCES gwapese.operating_copy (app_name,
    lang_tag, original) ON DELETE CASCADE ON UPDATE RESTRICT
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'specialization_name');

CREATE TABLE gwapese.specialization_name_history (
  LIKE gwapese.specialization_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'specialization_name', 'specialization_name_history');

COMMIT;
