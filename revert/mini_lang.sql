-- Revert gwapo-db:mini_lang from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'mini_name_context');

DROP TABLE gwapese.mini_name_context_history;

DROP TABLE gwapese.mini_name_context;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'mini_name');

DROP TABLE gwapese.mini_name_history;

DROP TABLE gwapese.mini_name;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'mini_unlock_context');

DROP TABLE gwapese.mini_unlock_context_history;

DROP TABLE gwapese.mini_unlock_context;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'mini_unlock');

DROP TABLE gwapese.mini_unlock_history;

DROP TABLE gwapese.mini_unlock;

COMMIT;
