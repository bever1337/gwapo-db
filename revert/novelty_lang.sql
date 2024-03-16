-- Revert gwapo-db:novelty_lang from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'novelty_description_context');

DROP TABLE gwapese.novelty_description_context_history;

DROP TABLE gwapese.novelty_description_context;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'novelty_description');

DROP TABLE gwapese.novelty_description_history;

DROP TABLE gwapese.novelty_description;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'novelty_name_context');

DROP TABLE gwapese.novelty_name_context_history;

DROP TABLE gwapese.novelty_name_context;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'novelty_name');

DROP TABLE gwapese.novelty_name_history;

DROP TABLE gwapese.novelty_name;

COMMIT;
