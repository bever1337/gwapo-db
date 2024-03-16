-- Revert gwapo-db:finisher_lang from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'finisher_detail_context');

DROP TABLE gwapese.finisher_detail_context_history;

DROP TABLE gwapese.finisher_detail_context;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'finisher_detail');

DROP TABLE gwapese.finisher_detail_history;

DROP TABLE gwapese.finisher_detail;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'finisher_name_context');

DROP TABLE gwapese.finisher_name_context_history;

DROP TABLE gwapese.finisher_name_context;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'finisher_name');

DROP TABLE gwapese.finisher_name_history;

DROP TABLE gwapese.finisher_name;

COMMIT;
