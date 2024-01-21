-- Deploy gawpo-db:finisher to pg
-- requires: schema
-- requires: history
-- requires: lang
BEGIN;

CREATE TABLE gwapese.finisher (
  finisher_id smallint NOT NULL,
  icon text NOT NULL,
  presentation_order smallint NOT NULL,
  CONSTRAINT finisher_pk PRIMARY KEY (finisher_id)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'finisher');

CREATE TABLE gwapese.finisher_history (
  LIKE gwapese.finisher
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'finisher', 'finisher_history');

CREATE TABLE gwapese.finisher_details (
  app_name text NOT NULL,
  finisher_id smallint NOT NULL,
  lang_tag text NOT NULL,
  original text NOT NULL,
  CONSTRAINT finisher_details_pk PRIMARY KEY (app_name, lang_tag, finisher_id),
  CONSTRAINT finisher_identifies_finisher_details_fk FOREIGN KEY (finisher_id)
    REFERENCES gwapese.finisher (finisher_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT operating_copy_precedes_finisher_details_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.operating_copy (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE RESTRICT
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'finisher_details');

CREATE TABLE gwapese.finisher_details_history (
  LIKE gwapese.finisher_details
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'finisher_details', 'finisher_details_history');

CREATE TABLE gwapese.finisher_name (
  app_name text NOT NULL,
  finisher_id smallint NOT NULL,
  lang_tag text NOT NULL,
  original text NOT NULL,
  CONSTRAINT finisher_name_pk PRIMARY KEY (app_name, lang_tag, finisher_id),
  CONSTRAINT finisher_identifies_finisher_name_fk FOREIGN KEY (finisher_id)
    REFERENCES gwapese.finisher (finisher_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT operating_copy_precedes_finisher_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.operating_copy (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE RESTRICT
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'finisher_name');

CREATE TABLE gwapese.finisher_name_history (
  LIKE gwapese.finisher_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'finisher_name', 'finisher_name_history');

COMMIT;
