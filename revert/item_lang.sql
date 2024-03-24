-- Revert gwapo-db:item_lang from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'item_description_context');

DROP TABLE gwapese.item_description_context_history;

DROP TABLE gwapese.item_description_context;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'item_description');

DROP TABLE gwapese.item_description_history;

DROP TABLE gwapese.item_description;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'item_name_context');

DROP TABLE gwapese.item_name_context_history;

DROP TABLE gwapese.item_name_context;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'item_name');

DROP TABLE gwapese.item_name_history;

DROP TABLE gwapese.item_name;

COMMIT;
