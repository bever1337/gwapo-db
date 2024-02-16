-- Deploy gwapo-db:guild_currency to pg
-- requires: schema
-- requires: history
-- requires: lang
BEGIN;

CREATE TABLE gwapese.guild_currency (
  guild_currency_id text NOT NULL,
  CONSTRAINT guild_currency_pk PRIMARY KEY (guild_currency_id)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'guild_currency');

CREATE TABLE gwapese.guild_currency_history (
  LIKE gwapese.guild_currency
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'guild_currency', 'guild_currency_history');

CREATE TABLE gwapese.guild_currency_description (
  app_name text NOT NULL,
  guild_currency_id text NOT NULL,
  lang_tag text NOT NULL,
  original text NOT NULL,
  CONSTRAINT guild_currency_description_pk PRIMARY KEY (app_name, lang_tag,
    guild_currency_id),
  CONSTRAINT guild_currency_identifies_guild_currency_description_fk FOREIGN
    KEY (guild_currency_id) REFERENCES gwapese.guild_currency
    (guild_currency_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT operating_copy_precedes_guild_currency_description_fk FOREIGN KEY
    (app_name, lang_tag, original) REFERENCES gwapese.operating_copy (app_name,
    lang_tag, original) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'guild_currency_description');

CREATE TABLE gwapese.guild_currency_description_history (
  LIKE gwapese.guild_currency_description
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'guild_currency_description', 'guild_currency_description_history');

CREATE TABLE gwapese.guild_currency_name (
  app_name text NOT NULL,
  guild_currency_id text NOT NULL,
  lang_tag text NOT NULL,
  original text NOT NULL,
  CONSTRAINT guild_currency_name_pk PRIMARY KEY (app_name, lang_tag, guild_currency_id),
  CONSTRAINT guild_currency_identifies_guild_currency_name_fk FOREIGN KEY
    (guild_currency_id) REFERENCES gwapese.guild_currency (guild_currency_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT operating_copy_precedes_guild_currency_name_fk FOREIGN KEY
    (app_name, lang_tag, original) REFERENCES gwapese.operating_copy (app_name,
    lang_tag, original) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'guild_currency_name');

CREATE TABLE gwapese.guild_currency_name_history (
  LIKE gwapese.guild_currency_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'guild_currency_name', 'guild_currency_name_history');

COMMIT;
