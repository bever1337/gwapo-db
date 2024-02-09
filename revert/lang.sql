-- Revert gwapo-db:lang from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'translated_copy');

DROP TABLE gwapese.translated_copy_history;

DROP TABLE gwapese.translated_copy;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'operating_copy');

DROP TABLE gwapese.operating_copy_history;

DROP TABLE gwapese.operating_copy;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'operating_lang');

DROP TABLE gwapese.operating_lang_history;

DROP TABLE gwapese.operating_lang;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'app');

DROP TABLE gwapese.app_history;

DROP TABLE gwapese.app;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'lang');

DROP TABLE gwapese.lang_history;

DROP TABLE gwapese.lang;

COMMIT;
