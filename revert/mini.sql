-- Revert gwapo-db:mini from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'mini_name');

DROP TABLE gwapese.mini_name_history;

DROP TABLE gwapese.mini_name;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'mini_unlock');

DROP TABLE gwapese.mini_unlock_history;

DROP TABLE gwapese.mini_unlock;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'mini');

DROP TABLE gwapese.mini_history;

DROP TABLE gwapese.mini;

COMMIT;
