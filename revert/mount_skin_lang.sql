-- Revert gwapo-db:mount_skin_lang from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'mount_skin_name_context');

DROP TABLE gwapese.mount_skin_name_context_history;

DROP TABLE gwapese.mount_skin_name_context;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'mount_skin_name');

DROP TABLE gwapese.mount_skin_name_history;

DROP TABLE gwapese.mount_skin_name;

COMMIT;
