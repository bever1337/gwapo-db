-- Revert gawpo-db:mount_skin from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'mount_skin_default');

DROP TABLE gwapese.mount_skin_default_history;

DROP TABLE gwapese.mount_skin_default;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'mount_skin_dye_slot');

DROP TABLE gwapese.mount_skin_dye_slot_history;

DROP TABLE gwapese.mount_skin_dye_slot;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'mount_skin_name');

DROP TABLE gwapese.mount_skin_name_history;

DROP TABLE gwapese.mount_skin_name;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'mount_skin');

DROP TABLE gwapese.mount_skin_history;

DROP TABLE gwapese.mount_skin;

COMMIT;
