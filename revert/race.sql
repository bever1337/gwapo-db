-- Revert gwapo-db:race from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'race_name');

DROP TABLE gwapese.race_name_history;

DROP TABLE gwapese.race_name;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'race');

DROP TABLE gwapese.race_history;

DROP TABLE gwapese.race;

COMMIT;
