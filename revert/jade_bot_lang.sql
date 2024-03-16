-- Revert gwapo-db:jade_bot_lang from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'jade_bot_description_context');

DROP TABLE gwapese.jade_bot_description_context_history;

DROP TABLE gwapese.jade_bot_description_context;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'jade_bot_description');

DROP TABLE gwapese.jade_bot_description_history;

DROP TABLE gwapese.jade_bot_description;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'jade_bot_name_context');

DROP TABLE gwapese.jade_bot_name_context_history;

DROP TABLE gwapese.jade_bot_name_context;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'jade_bot_name');

DROP TABLE gwapese.jade_bot_name_history;

DROP TABLE gwapese.jade_bot_name;

COMMIT;
