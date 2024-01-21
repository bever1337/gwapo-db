-- Deploy gawpo-db:mini to pg
-- requires: schema
-- requires: history
-- requires: lang
BEGIN;

CREATE TABLE gwapese.mini (
  icon text NOT NULL,
  mini_id smallint NOT NULL,
  item_id smallint NOT NULL,
  presentation_order smallint NOT NULL,
  CONSTRAINT mini_pk PRIMARY KEY (mini_id)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'mini');

CREATE TABLE gwapese.mini_history (
  LIKE gwapese.mini
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'mini', 'mini_history');

CREATE TABLE gwapese.mini_name (
  app_name text NOT NULL,
  lang_tag text NOT NULL,
  mini_id smallint NOT NULL,
  original text NOT NULL,
  CONSTRAINT mini_name_pk PRIMARY KEY (app_name, lang_tag, mini_id),
  CONSTRAINT mini_identifies_mini_name_fk FOREIGN KEY (mini_id) REFERENCES
    gwapese.mini (mini_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT operating_copy_precedes_mini_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.operating_copy (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE RESTRICT
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'mini_name');

CREATE TABLE gwapese.mini_name_history (
  LIKE gwapese.mini_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'mini_name', 'mini_name_history');

CREATE TABLE gwapese.mini_unlock (
  app_name text NOT NULL,
  lang_tag text NOT NULL,
  mini_id smallint NOT NULL,
  original text NOT NULL,
  CONSTRAINT mini_unlock_pk PRIMARY KEY (app_name, lang_tag, mini_id),
  CONSTRAINT mini_identifies_mini_unlock_fk FOREIGN KEY (mini_id) REFERENCES
    gwapese.mini (mini_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT operating_copy_precedes_mini_unlock_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.operating_copy (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE RESTRICT
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'mini_unlock');

CREATE TABLE gwapese.mini_unlock_history (
  LIKE gwapese.mini_unlock
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'mini_unlock', 'mini_unlock_history');

COMMIT;
