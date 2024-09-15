-- Revert gwapo-db:lang from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'copy_target');

DROP TABLE gwapese.copy_target_history;

DROP TABLE gwapese.copy_target;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'copy_source');

DROP TABLE gwapese.copy_source_history;

DROP TABLE gwapese.copy_source;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'operating_lang');

DROP TABLE gwapese.operating_lang_history;

DROP TABLE gwapese.operating_lang;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'copy_document');

DROP TABLE gwapese.copy_document_history;

DROP TABLE gwapese.copy_document;

DROP FUNCTION gwapese.xml_to_text;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'app');

DROP TABLE gwapese.app_history;

DROP TABLE gwapese.app;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'lang');

DROP TABLE gwapese.lang_history;

DROP TABLE gwapese.lang;

COMMIT;
