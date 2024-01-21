-- Revert gawpo-db:profession from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'profession_name');

DROP TABLE gwapese.profession_name_history;

DROP TABLE gwapese.profession_name;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'profession');

DROP TABLE gwapese.profession_history;

DROP TABLE gwapese.profession;

COMMIT;
