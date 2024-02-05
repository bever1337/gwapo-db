-- Deploy gawpo-db:jade_bot_item to pg
-- requires: schema
-- requires: history
-- requires: jade_bot
-- requires: item
BEGIN;

CREATE TABLE gwapese.jade_bot_item (
  item_id integer NOT NULL,
  jade_bot_id integer NOT NULL,
  CONSTRAINT jade_bot_item_pk PRIMARY KEY (jade_bot_id, item_id),
  CONSTRAINT jade_bot_identifies_jade_bot_item_fk FOREIGN KEY (jade_bot_id)
    REFERENCES gwapese.jade_bot (jade_bot_id),
  CONSTRAINT item_identifies_jade_bot_item_fk FOREIGN KEY (item_id) REFERENCES
    gwapese.item (item_id)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'jade_bot_item');

CREATE TABLE gwapese.jade_bot_item_history (
  LIKE gwapese.jade_bot_item
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'jade_bot_item', 'jade_bot_item_history');

COMMIT;
