-- Revert gwapo-db:novelty from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'novelty_description');

DROP TABLE gwapese.novelty_description_history;

DROP TABLE gwapese.novelty_description;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'novelty_name');

DROP TABLE gwapese.novelty_name_history;

DROP TABLE gwapese.novelty_name;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'novelty');

DROP TABLE gwapese.novelty_history;

DROP TABLE gwapese.novelty;

COMMIT;
