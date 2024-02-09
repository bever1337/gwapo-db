-- Revert gwapo-db:mount from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'mount_name');

DROP TABLE gwapese.mount_name_history;

DROP TABLE gwapese.mount_name;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'mount');

DROP TABLE gwapese.mount_history;

DROP TABLE gwapese.mount;

COMMIT;
