-- Deploy gawpo-db:novelty_item to pg
-- requires: schema
-- requires: history
-- requires: novelty
-- requires: item
BEGIN;

CREATE TABLE gwapese.novelty_item (
  item_id integer NOT NULL,
  novelty_id integer NOT NULL,
  CONSTRAINT novelty_item_pk PRIMARY KEY (novelty_id, item_id),
  CONSTRAINT novelty_identifies_novelty_item_fk FOREIGN KEY (novelty_id)
    REFERENCES gwapese.novelty (novelty_id),
  CONSTRAINT item_identifies_novelty_item_fk FOREIGN KEY (item_id) REFERENCES
    gwapese.item (item_id)
);

CALL temporal_tables.alter_table_to_temporal ('gwapese', 'novelty_item');

CREATE TABLE gwapese.novelty_item_history (
  LIKE gwapese.novelty_item
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'novelty_item', 'novelty_item_history');

COMMIT;
