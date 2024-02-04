-- Deploy gawpo-db:guild_upgrade to pg
-- requires: schema
-- requires: history
-- requires: lang
BEGIN;

CREATE TABLE gwapese.guild_upgrade (
  build_time integer NOT NULL,
  experience integer NOT NULL,
  guild_upgrade_id integer NOT NULL,
  guild_upgrade_type text NOT NULL,
  icon text NOT NULL,
  required_level integer NOT NULL,
  CONSTRAINT guild_upgrade_pk PRIMARY KEY (guild_upgrade_id)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'guild_upgrade');

CREATE TABLE gwapese.guild_upgrade_history (
  LIKE gwapese.guild_upgrade
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'guild_upgrade', 'guild_upgrade_history');

CREATE TABLE gwapese.guild_upgrade_description (
  app_name text NOT NULL,
  guild_upgrade_id integer NOT NULL,
  lang_tag text NOT NULL,
  original text NOT NULL,
  CONSTRAINT guild_upgrade_description_pk PRIMARY KEY (app_name, lang_tag,
    guild_upgrade_id),
  CONSTRAINT guild_upgrade_identifies_guild_upgrade_description_fk FOREIGN KEY
    (guild_upgrade_id) REFERENCES gwapese.guild_upgrade (guild_upgrade_id) ON
    DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT operating_copy_precedes_guild_upgrade_description_fk FOREIGN KEY
    (app_name, lang_tag, original) REFERENCES gwapese.operating_copy (app_name,
    lang_tag, original) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'guild_upgrade_description');

CREATE TABLE gwapese.guild_upgrade_description_history (
  LIKE gwapese.guild_upgrade_description
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'guild_upgrade_description', 'guild_upgrade_description_history');

CREATE TABLE gwapese.guild_upgrade_name (
  app_name text NOT NULL,
  guild_upgrade_id integer NOT NULL,
  lang_tag text NOT NULL,
  original text NOT NULL,
  CONSTRAINT guild_upgrade_name_pk PRIMARY KEY (app_name, lang_tag, guild_upgrade_id),
  CONSTRAINT guild_upgrade_identifies_guild_upgrade_name_fk FOREIGN KEY
    (guild_upgrade_id) REFERENCES gwapese.guild_upgrade (guild_upgrade_id) ON
    DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT operating_copy_precedes_guild_upgrade_name_fk FOREIGN KEY
    (app_name, lang_tag, original) REFERENCES gwapese.operating_copy (app_name,
    lang_tag, original) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'guild_upgrade_name');

CREATE TABLE gwapese.guild_upgrade_name_history (
  LIKE gwapese.guild_upgrade_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'guild_upgrade_name', 'guild_upgrade_name_history');

CREATE TABLE gwapese.guild_upgrade_prerequisite (
  guild_upgrade_id integer NOT NULL,
  prerequisite_guild_upgrade_id integer NOT NULL,
  CONSTRAINT guild_upgrade_prerequisite_pk PRIMARY KEY (guild_upgrade_id,
    prerequisite_guild_upgrade_id),
  CONSTRAINT guild_upgrade_identifies_guild_upgrade_prerequisite_fk FOREIGN KEY
    (guild_upgrade_id) REFERENCES gwapese.guild_upgrade (guild_upgrade_id) ON
    DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT guild_upgrade_identifies_guild_upgrade_prerequisites_fk FOREIGN
    KEY (prerequisite_guild_upgrade_id) REFERENCES gwapese.guild_upgrade
    (guild_upgrade_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'guild_upgrade_prerequisite');

CREATE TABLE gwapese.guild_upgrade_prerequisite_history (
  LIKE gwapese.guild_upgrade_prerequisite
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'guild_upgrade_prerequisite', 'guild_upgrade_prerequisite_history');

-- TODO guild costs references item, collectible, currency, coin
COMMIT;
