-- Deploy gwapo-db:finisher_item to pg
-- requires: schema
-- requires: history
-- requires: finisher
-- requires: item
BEGIN;

CREATE TABLE gwapese.finisher_item (
  finisher_id integer NOT NULL,
  item_id integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT finisher_item_pk PRIMARY KEY (finisher_id, item_id),
  CONSTRAINT finisher_identifies_item_fk FOREIGN KEY (finisher_id) REFERENCES
    gwapese.finisher (finisher_id),
  CONSTRAINT item_identifies_finisher_item_fk FOREIGN KEY (item_id) REFERENCES
    gwapese.item (item_id)
);

CREATE TABLE gwapese.finisher_item_history (
  LIKE gwapese.finisher_item
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'finisher_item', 'finisher_item_history');

COMMIT;
