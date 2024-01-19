-- Revert gawpo-db:skin__back from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_back');

DROP TABLE gwapese.skin_back_history;

DROP TABLE gwapese.skin_back;

COMMIT;
