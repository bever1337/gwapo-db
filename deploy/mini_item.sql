-- Deploy gwapo-db:mini_item to pg
-- requires: schema
-- requires: history
-- requires: mini
-- requires: item
BEGIN;

CREATE TABLE gwapese.mini_item (
  item_id integer NOT NULL,
  mini_id integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT mini_item_pk PRIMARY KEY (mini_id, item_id),
  CONSTRAINT mini_identifies_item_fk FOREIGN KEY (mini_id) REFERENCES
    gwapese.mini (mini_id),
  CONSTRAINT item_identifies_mini_item_fk FOREIGN KEY (item_id) REFERENCES
    gwapese.item (item_id)
);

CREATE TABLE gwapese.mini_item_history (
  LIKE gwapese.mini_item
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'mini_item', 'mini_item_history');

COMMIT;
