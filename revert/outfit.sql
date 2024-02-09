-- Revert gwapo-db:outfit from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'outfit_name');

DROP TABLE gwapese.outfit_name_history;

DROP TABLE gwapese.outfit_name;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'outfit');

DROP TABLE gwapese.outfit_history;

DROP TABLE gwapese.outfit;

COMMIT;
