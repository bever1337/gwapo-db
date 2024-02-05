-- Deploy gawpo-db:emote to pg
-- requires: schema
-- requires: history
BEGIN;

CREATE TABLE gwapese.emote (
  emote_id text NOT NULL,
  CONSTRAINT emote_pk PRIMARY KEY (emote_id)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'emote');

CREATE TABLE gwapese.emote_history (
  LIKE gwapese.emote
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'emote', 'emote_history');

CREATE TABLE gwapese.emote_command (
  command text NOT NULL,
  emote_id text NOT NULL,
  CONSTRAINT emote_command_pk PRIMARY KEY (emote_id, command),
  CONSTRAINT emote_identifies_emote_command_fk FOREIGN KEY (emote_id)
    REFERENCES gwapese.emote (emote_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'emote_command');

CREATE TABLE gwapese.emote_command_history (
  LIKE gwapese.emote_command
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'emote_command', 'emote_command_history');

COMMIT;
