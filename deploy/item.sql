-- Deploy gwapo-db:item to pg
-- requires: schema
-- requires: history
BEGIN;

CREATE TABLE gwapese.item (
  chat_link text NOT NULL,
  icon text,
  item_id integer NOT NULL,
  rarity text NOT NULL,
  required_level integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  vendor_value bigint NOT NULL,
  CONSTRAINT item_pk PRIMARY KEY (item_id)
);

CREATE TABLE gwapese.item_history (
  LIKE gwapese.item
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'item', 'item_history');

CREATE TABLE gwapese.item_flag (
  flag text NOT NULL,
  item_id integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT item_flag_pk PRIMARY KEY (item_id, flag),
  CONSTRAINT item_identifies_flag_fk FOREIGN KEY (item_id) REFERENCES
    gwapese.item (item_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.item_flag_history (
  LIKE gwapese.item_flag
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'item_flag', 'item_flag_history');

CREATE TABLE gwapese.item_game_type (
  game_type text NOT NULL,
  item_id integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT item_game_type_pk PRIMARY KEY (item_id, game_type),
  CONSTRAINT item_identifies_game_type_fk FOREIGN KEY (item_id) REFERENCES
    gwapese.item (item_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.item_game_type_history (
  LIKE gwapese.item_game_type
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'item_game_type', 'item_game_type_history');

CREATE TABLE gwapese.item_restriction_profession (
  item_id integer NOT NULL,
  profession_id text NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT item_restriction_profession_pk PRIMARY KEY (item_id, profession_id),
  CONSTRAINT item_identifies_restriction_profession_fk FOREIGN KEY (item_id)
    REFERENCES gwapese.item (item_id) ON DELETE CASCADE,
  CONSTRAINT profession_enumerates_item_restriction_profession_fk FOREIGN KEY
    (profession_id) REFERENCES gwapese.profession (profession_id) ON DELETE
    CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.item_restriction_profession_history (
  LIKE gwapese.item_restriction_profession
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'item_restriction_profession', 'item_restriction_profession_history');

CREATE TABLE gwapese.item_restriction_race (
  item_id integer NOT NULL,
  race_id text NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT item_restriction_race_pk PRIMARY KEY (item_id, race_id),
  CONSTRAINT item_identifies_restriction_race_fk FOREIGN KEY (item_id)
    REFERENCES gwapese.item (item_id) ON DELETE CASCADE,
  CONSTRAINT race_enumerates_item_restriction_race_fk FOREIGN KEY (race_id)
    REFERENCES gwapese.race (race_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.item_restriction_race_history (
  LIKE gwapese.item_restriction_race
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'item_restriction_race', 'item_restriction_race_history');

CREATE TABLE gwapese.item_type (
  item_id integer UNIQUE NOT NULL,
  item_type text NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT item_type_pk PRIMARY KEY (item_id, item_type),
  CONSTRAINT item_identifies_type_fk FOREIGN KEY (item_id) REFERENCES
    gwapese.item (item_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.item_type_history (
  LIKE gwapese.item_type
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'item_type', 'item_type_history');

CREATE TABLE gwapese.item_upgrade (
  from_item_id integer NOT NULL,
  to_item_id integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  upgrade text NOT NULL,
  CONSTRAINT item_upgrade_from_pk PRIMARY KEY (from_item_id, to_item_id, upgrade),
  CONSTRAINT item_identifies_upgrade_from_fk FOREIGN KEY (from_item_id)
    REFERENCES gwapese.item (item_id),
  CONSTRAINT item_identifies_upgrade_to_fk FOREIGN KEY (to_item_id) REFERENCES
    gwapese.item (item_id)
);

CREATE TABLE gwapese.item_upgrade_history (
  LIKE gwapese.item_upgrade
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'item_upgrade', 'item_upgrade_history');

COMMIT;
