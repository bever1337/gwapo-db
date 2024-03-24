-- Revert gwapo-db:profession from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'profession');

DROP TABLE gwapese.profession_history;

DROP TABLE gwapese.profession;

COMMIT;
