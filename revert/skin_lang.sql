-- Revert gwapo-db:skin_lang from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_description_context');

DROP TABLE gwapese.skin_description_context_history;

DROP TABLE gwapese.skin_description_context;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_description');

DROP TABLE gwapese.skin_description_history;

DROP TABLE gwapese.skin_description;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_name_context');

DROP TABLE gwapese.skin_name_context_history;

DROP TABLE gwapese.skin_name_context;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_name');

DROP TABLE gwapese.skin_name_history;

DROP TABLE gwapese.skin_name;

COMMIT;
