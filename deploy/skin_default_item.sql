-- Deploy gwapo-db:skin_default_item to pg
-- requires: schema
-- requires: history
-- requires: skin
-- requires: item
BEGIN;

CREATE TABLE gwapese.skin_default_item (
  item_id integer UNIQUE NOT NULL,
  skin_id integer NOT NULL,
  sysrange_lower timestamp(3) NOT NULL,
  sysrange_upper timestamp(3) NOT NULL,
  CONSTRAINT skin_default_item_pk PRIMARY KEY (skin_id, item_id),
  CONSTRAINT skin_identifies_default_item_fk FOREIGN KEY (skin_id) REFERENCES
    gwapese.skin (skin_id),
  CONSTRAINT item_identifies_skin_default_item_fk FOREIGN KEY (item_id)
    REFERENCES gwapese.item (item_id)
);

CREATE TABLE gwapese.skin_default_item_history (
  LIKE gwapese.skin_default_item
);

CALL temporal_tables.create_historicize_trigger ('gwapese',
  'skin_default_item', 'skin_default_item_history');

COMMIT;
