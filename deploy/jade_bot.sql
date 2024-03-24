-- Deploy gwapo-db:jade_bot to pg
-- requires: schema
-- requires: history
BEGIN;

CREATE TABLE gwapese.jade_bot (
  jade_bot_id integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT jade_bot_pk PRIMARY KEY (jade_bot_id)
);

CREATE TABLE gwapese.jade_bot_history (
  LIKE gwapese.jade_bot
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'jade_bot', 'jade_bot_history');

COMMIT;
