-- Deploy gawpo-db:outfit to pg
-- requires: schema
-- requires: history
-- requires: lang
BEGIN;

CREATE TABLE gwapese.outfit (
  icon text NOT NULL,
  outfit_id smallint NOT NULL,
  CONSTRAINT outfit_pk PRIMARY KEY (outfit_id)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'outfit');

CREATE TABLE gwapese.outfit_history (
  LIKE gwapese.outfit
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'outfit', 'outfit_history');

CREATE TABLE gwapese.outfit_name (
  app_name text NOT NULL,
  lang_tag text NOT NULL,
  original text NOT NULL,
  outfit_id smallint NOT NULL,
  CONSTRAINT outfit_name_pk PRIMARY KEY (app_name, lang_tag, outfit_id),
  CONSTRAINT outfit_identifies_outfit_name_fk FOREIGN KEY (outfit_id)
    REFERENCES gwapese.outfit (outfit_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT operating_copy_precedes_outfit_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.operating_copy (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE RESTRICT
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'outfit_name');

CREATE TABLE gwapese.outfit_name_history (
  LIKE gwapese.outfit_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'outfit_name', 'outfit_name_history');

-- todo references unlock_item(s)
COMMIT;
