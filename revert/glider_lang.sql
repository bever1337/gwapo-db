-- Revert gwapo-db:glider_lang from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'glider_description_context');

DROP TABLE gwapese.glider_description_context_history;

DROP TABLE gwapese.glider_description_context;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'glider_description');

DROP TABLE gwapese.glider_description_history;

DROP TABLE gwapese.glider_description;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'glider_name_context');

DROP TABLE gwapese.glider_name_context_history;

DROP TABLE gwapese.glider_name_context;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'glider_name');

DROP TABLE gwapese.glider_name_history;

DROP TABLE gwapese.glider_name;

COMMIT;
