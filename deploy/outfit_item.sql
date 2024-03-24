-- Deploy gwapo-db:outfit_item to pg
-- requires: schema
-- requires: history
-- requires: outfit
-- requires: item
BEGIN;

CREATE TABLE gwapese.outfit_item (
  item_id integer NOT NULL,
  outfit_id integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT outfit_item_pk PRIMARY KEY (outfit_id, item_id),
  CONSTRAINT outfit_identifies_item_fk FOREIGN KEY (outfit_id) REFERENCES
    gwapese.outfit (outfit_id),
  CONSTRAINT item_identifies_outfit_item_fk FOREIGN KEY (item_id) REFERENCES
    gwapese.item (item_id)
);

CREATE TABLE gwapese.outfit_item_history (
  LIKE gwapese.outfit_item
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'outfit_item', 'outfit_item_history');

COMMIT;
