-- Revert gawpo-db:finisher from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'finisher_details');

DROP TABLE gwapese.finisher_details_history;

DROP TABLE gwapese.finisher_details;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'finisher_name');

DROP TABLE gwapese.finisher_name_history;

DROP TABLE gwapese.finisher_name;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'finisher');

DROP TABLE gwapese.finisher_history;

DROP TABLE gwapese.finisher;

COMMIT;
