-- Revert gawpo-db:glider from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'glider_description');

DROP TABLE gwapese.glider_description_history;

DROP TABLE gwapese.glider_description;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'glider_dye');

DROP TABLE gwapese.glider_dye_history;

DROP TABLE gwapese.glider_dye;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'glider_name');

DROP TABLE gwapese.glider_name_history;

DROP TABLE gwapese.glider_name;

-- CALL temporal_tables.drop_historicize_fn ('gwapese', 'glider_unlock');
-- DROP TABLE gwapese.glider_unlock_history;
-- DROP TABLE gwapese.glider_unlock;
CALL temporal_tables.drop_historicize_fn ('gwapese', 'glider');

DROP TABLE gwapese.glider_history;

DROP TABLE gwapese.glider;

COMMIT;
