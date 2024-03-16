-- Deploy gwapo-db:emote_item to pg
-- requires: schema
-- requires: history
-- requires: emote
-- requires: item
BEGIN;

CREATE TABLE gwapese.emote_item (
  emote_id text NOT NULL,
  item_id integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT emote_item_pk PRIMARY KEY (emote_id, item_id),
  CONSTRAINT emote_identifies_item_fk FOREIGN KEY (emote_id) REFERENCES
    gwapese.emote (emote_id),
  CONSTRAINT item_identifies_emote_item_fk FOREIGN KEY (item_id) REFERENCES
    gwapese.item (item_id)
);

CREATE TABLE gwapese.emote_item_history (
  LIKE gwapese.emote_item
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'emote_item', 'emote_item_history');

COMMIT;
