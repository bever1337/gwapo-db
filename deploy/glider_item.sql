-- Deploy gwapo-db:glider_item to pg
-- requires: schema
-- requires: history
-- requires: glider
-- requires: item
BEGIN;

CREATE TABLE gwapese.glider_item (
  glider_id integer NOT NULL,
  item_id integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT glider_item_pk PRIMARY KEY (glider_id, item_id),
  CONSTRAINT glider_identifies_item_fk FOREIGN KEY (glider_id) REFERENCES
    gwapese.glider (glider_id),
  CONSTRAINT item_identifies_glider_item_fk FOREIGN KEY (item_id) REFERENCES
    gwapese.item (item_id)
);

CREATE TABLE gwapese.glider_item_history (
  LIKE gwapese.glider_item
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'glider_item', 'glider_item_history');

COMMIT;
