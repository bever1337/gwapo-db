-- Revert gawpo-db:skin_gathering from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_gathering');

DROP TABLE gwapese.skin_gathering_history;

DROP TABLE gwapese.skin_gathering;

COMMIT;
