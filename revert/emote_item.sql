-- Revert gawpo-db:emote_item from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'emote_item');

DROP TABLE gwapese.emote_item_history;

DROP TABLE gwapese.emote_item;

COMMIT;
