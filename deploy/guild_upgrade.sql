-- Deploy gwapo-db:guild_upgrade to pg
-- requires: schema
-- requires: history
BEGIN;

CREATE TABLE gwapese.guild_upgrade (
  build_time integer NOT NULL,
  experience integer NOT NULL,
  guild_upgrade_id integer NOT NULL,
  guild_upgrade_type text NOT NULL,
  icon text NOT NULL,
  required_level integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT guild_upgrade_pk PRIMARY KEY (guild_upgrade_id)
);

CREATE TABLE gwapese.guild_upgrade_history (
  LIKE gwapese.guild_upgrade
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'guild_upgrade', 'guild_upgrade_history');

CREATE TABLE gwapese.guild_upgrade_prerequisite (
  guild_upgrade_id integer NOT NULL,
  prerequisite_guild_upgrade_id integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT guild_upgrade_prerequisite_pk PRIMARY KEY (guild_upgrade_id,
    prerequisite_guild_upgrade_id),
  CONSTRAINT guild_upgrade_identifies_requisite_fk FOREIGN KEY
    (guild_upgrade_id) REFERENCES gwapese.guild_upgrade (guild_upgrade_id) ON
    DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT guild_upgrade_identifies_prerequisite_fk FOREIGN KEY
    (prerequisite_guild_upgrade_id) REFERENCES gwapese.guild_upgrade
    (guild_upgrade_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE gwapese.guild_upgrade_prerequisite_history (
  LIKE gwapese.guild_upgrade_prerequisite
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'guild_upgrade_prerequisite', 'guild_upgrade_prerequisite_history');

COMMIT;
