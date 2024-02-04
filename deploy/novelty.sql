-- Deploy gawpo-db:novelty to pg
-- requires: schema
-- requires: history
-- requires: lang
BEGIN;

CREATE TABLE gwapese.novelty (
  icon text NOT NULL,
  novelty_id integer NOT NULL,
  slot text NOT NULL,
  CONSTRAINT novelty_pk PRIMARY KEY (novelty_id)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'novelty');

CREATE TABLE gwapese.novelty_history (
  LIKE gwapese.novelty
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'novelty', 'novelty_history');

CREATE TABLE gwapese.novelty_description (
  app_name text NOT NULL,
  lang_tag text NOT NULL,
  novelty_id integer NOT NULL,
  original text NOT NULL,
  CONSTRAINT novelty_description_pk PRIMARY KEY (app_name, lang_tag, novelty_id),
  CONSTRAINT novelty_identifies_novelty_description_fk FOREIGN KEY (novelty_id)
    REFERENCES gwapese.novelty (novelty_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT operating_copy_precedes_novelty_description_fk FOREIGN KEY
    (app_name, lang_tag, original) REFERENCES gwapese.operating_copy (app_name,
    lang_tag, original) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'novelty_description');

CREATE TABLE gwapese.novelty_description_history (
  LIKE gwapese.novelty_description
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'novelty_description', 'novelty_description_history');

CREATE TABLE gwapese.novelty_name (
  app_name text NOT NULL,
  lang_tag text NOT NULL,
  novelty_id integer NOT NULL,
  original text NOT NULL,
  CONSTRAINT novelty_name_pk PRIMARY KEY (app_name, lang_tag, novelty_id),
  CONSTRAINT novelty_identifies_novelty_name_fk FOREIGN KEY (novelty_id)
    REFERENCES gwapese.novelty (novelty_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT operating_copy_precedes_novelty_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.operating_copy (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'novelty_name');

CREATE TABLE gwapese.novelty_name_history (
  LIKE gwapese.novelty_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'novelty_name', 'novelty_name_history');

-- todo references unlock_item(s)
COMMIT;
