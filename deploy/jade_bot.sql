-- Deploy gawpo-db:jade_bot to pg
-- requires: schema
-- requires: history
-- requires: lang
BEGIN;

CREATE TABLE gwapese.jade_bot (
  jade_bot_id smallint NOT NULL,
  CONSTRAINT jade_bot_pk PRIMARY KEY (jade_bot_id)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'jade_bot');

CREATE TABLE gwapese.jade_bot_history (
  LIKE gwapese.jade_bot
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'jade_bot', 'jade_bot_history');

CREATE TABLE gwapese.jade_bot_description (
  app_name text NOT NULL,
  jade_bot_id smallint NOT NULL,
  lang_tag text NOT NULL,
  original text NOT NULL,
  CONSTRAINT jade_bot_description_pk PRIMARY KEY (app_name, lang_tag, jade_bot_id),
  CONSTRAINT jade_bot_identifies_jade_bot_description_fk FOREIGN KEY
    (jade_bot_id) REFERENCES gwapese.jade_bot (jade_bot_id) ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT operating_copy_precedes_jade_bot_description_fk FOREIGN KEY
    (app_name, lang_tag, original) REFERENCES gwapese.operating_copy (app_name,
    lang_tag, original) ON DELETE CASCADE ON UPDATE RESTRICT
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'jade_bot_description');

CREATE TABLE gwapese.jade_bot_description_history (
  LIKE gwapese.jade_bot_description
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'jade_bot_description', 'jade_bot_description_history');

CREATE TABLE gwapese.jade_bot_name (
  app_name text NOT NULL,
  jade_bot_id smallint NOT NULL,
  lang_tag text NOT NULL,
  original text NOT NULL,
  CONSTRAINT jade_bot_name_pk PRIMARY KEY (app_name, lang_tag, jade_bot_id),
  CONSTRAINT jade_bot_identifies_jade_bot_name_fk FOREIGN KEY (jade_bot_id)
    REFERENCES gwapese.jade_bot (jade_bot_id) ON DELETE CASCADE ON UPDATE
    CASCADE,
  CONSTRAINT operating_copy_precedes_jade_bot_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.operating_copy (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE RESTRICT
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'jade_bot_name');

CREATE TABLE gwapese.jade_bot_name_history (
  LIKE gwapese.jade_bot_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'jade_bot_name', 'jade_bot_name_history');

COMMIT;
