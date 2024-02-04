-- Revert gawpo-db:jade_bot from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'jade_bot_description');

DROP TABLE gwapese.jade_bot_description_history;

DROP TABLE gwapese.jade_bot_description;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'jade_bot_name');

DROP TABLE gwapese.jade_bot_name_history;

DROP TABLE gwapese.jade_bot_name;

-- CALL temporal_tables.drop_historicize_fn ('gwapese', 'jade_bot_unlock');
-- DROP TABLE gwapese.jade_bot_unlock_history;
-- DROP TABLE gwapese.jade_bot_unlock;
CALL temporal_tables.drop_historicize_fn ('gwapese', 'jade_bot');

DROP TABLE gwapese.jade_bot_history;

DROP TABLE gwapese.jade_bot;

COMMIT;
