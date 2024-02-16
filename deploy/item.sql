-- Deploy gwapo-db:item to pg
-- requires: schema
-- requires: history
-- requires: lang
BEGIN;

CREATE TABLE gwapese.item (
  chat_link text NOT NULL,
  icon text,
  item_id integer NOT NULL,
  rarity text NOT NULL,
  required_level integer NOT NULL,
  vendor_value bigint NOT NULL,
  CONSTRAINT item_pk PRIMARY KEY (item_id)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'item');

CREATE TABLE gwapese.item_history (
  LIKE gwapese.item
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'item', 'item_history');

CREATE TABLE gwapese.item_description (
  app_name text NOT NULL,
  item_id integer NOT NULL,
  lang_tag text NOT NULL,
  original text NOT NULL,
  CONSTRAINT item_description_pk PRIMARY KEY (app_name, lang_tag, item_id),
  CONSTRAINT item_identifies_item_description_fk FOREIGN KEY (item_id)
    REFERENCES gwapese.item (item_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT operating_copy_precedes_item_description_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.operating_copy (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'item_description');

CREATE TABLE gwapese.item_description_history (
  LIKE gwapese.item_description
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'item_description', 'item_description_history');

CREATE TABLE gwapese.item_flag (
  flag text NOT NULL,
  item_id integer NOT NULL,
  CONSTRAINT item_flag_pk PRIMARY KEY (item_id, flag),
  CONSTRAINT item_identifies_item_flag_fk FOREIGN KEY (item_id) REFERENCES
    gwapese.item (item_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'item_flag');

CREATE TABLE gwapese.item_flag_history (
  LIKE gwapese.item_flag
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'item_flag', 'item_flag_history');

CREATE TABLE gwapese.item_game_type (
  game_type text NOT NULL,
  item_id integer NOT NULL,
  CONSTRAINT item_game_type_pk PRIMARY KEY (item_id, game_type),
  CONSTRAINT item_identifies_item_game_type_fk FOREIGN KEY (item_id) REFERENCES
    gwapese.item (item_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'item_game_type');

CREATE TABLE gwapese.item_game_type_history (
  LIKE gwapese.item_game_type
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'item_game_type', 'item_game_type_history');

CREATE TABLE gwapese.item_name (
  app_name text NOT NULL,
  item_id integer NOT NULL,
  lang_tag text NOT NULL,
  original text NOT NULL,
  CONSTRAINT item_name_pk PRIMARY KEY (app_name, lang_tag, item_id),
  CONSTRAINT item_identifies_item_name_fk FOREIGN KEY (item_id) REFERENCES
    gwapese.item (item_id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT operating_copy_precedes_item_name_fk FOREIGN KEY (app_name,
    lang_tag, original) REFERENCES gwapese.operating_copy (app_name, lang_tag,
    original) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'item_name');

CREATE TABLE gwapese.item_name_history (
  LIKE gwapese.item_name
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'item_name', 'item_name_history');

CREATE TABLE gwapese.item_restriction_profession (
  item_id integer NOT NULL,
  profession_id text NOT NULL,
  CONSTRAINT item_restriction_profession_pk PRIMARY KEY (item_id, profession_id),
  CONSTRAINT item_identifies_item_restriction_profession_fk FOREIGN KEY
    (item_id) REFERENCES gwapese.item (item_id) ON DELETE CASCADE,
  CONSTRAINT profession_enumerates_item_restriction_profession_fk FOREIGN KEY
    (profession_id) REFERENCES gwapese.profession (profession_id) ON DELETE
    CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'item_restriction_profession');

CREATE TABLE gwapese.item_restriction_profession_history (
  LIKE gwapese.item_restriction_profession
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'item_restriction_profession', 'item_restriction_profession_history');

CREATE TABLE gwapese.item_restriction_race (
  item_id integer NOT NULL,
  race_id text NOT NULL,
  CONSTRAINT item_restriction_race_pk PRIMARY KEY (item_id, race_id),
  CONSTRAINT item_identifies_item_restriction_race_fk FOREIGN KEY (item_id)
    REFERENCES gwapese.item (item_id) ON DELETE CASCADE,
  CONSTRAINT race_enumerates_item_restriction_race_fk FOREIGN KEY (race_id)
    REFERENCES gwapese.race (race_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'item_restriction_race');

CREATE TABLE gwapese.item_restriction_race_history (
  LIKE gwapese.item_restriction_race
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'item_restriction_race', 'item_restriction_race_history');

CREATE TABLE gwapese.item_type (
  item_id integer UNIQUE NOT NULL,
  item_type text NOT NULL,
  CONSTRAINT item_type_pk PRIMARY KEY (item_id, item_type),
  CONSTRAINT item_identifies_item_type_fk FOREIGN KEY (item_id) REFERENCES
    gwapese.item (item_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'item_type');

CREATE TABLE gwapese.item_type_history (
  LIKE gwapese.item_type
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'item_type', 'item_type_history');

CREATE TABLE gwapese.item_upgrade (
  from_item_id integer NOT NULL,
  to_item_id integer NOT NULL,
  upgrade text NOT NULL,
  CONSTRAINT item_upgrade_from_pk PRIMARY KEY (from_item_id, to_item_id, upgrade),
  CONSTRAINT item_identifies_item_upgrade_from_fk FOREIGN KEY (from_item_id)
    REFERENCES gwapese.item (item_id),
  CONSTRAINT item_identifies_item_upgrade_to_fk FOREIGN KEY (to_item_id)
    REFERENCES gwapese.item (item_id)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'item_upgrade');

CREATE TABLE gwapese.item_upgrade_history (
  LIKE gwapese.item_upgrade
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'item_upgrade', 'item_upgrade_history');

COMMIT;
