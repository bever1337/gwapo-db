-- Revert gawpo-db:skins from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_description');

DROP TABLE gwapese.skin_description_history;

DROP TABLE gwapese.skin_description;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_flag');

DROP TABLE gwapese.skin_flag_history;

DROP TABLE gwapese.skin_flag;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_name');

DROP TABLE gwapese.skin_name_history;

DROP TABLE gwapese.skin_name;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_restriction');

DROP TABLE gwapese.skin_restriction_history;

DROP TABLE gwapese.skin_restriction;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_type');

DROP TABLE gwapese.skin_type_history;

DROP TABLE gwapese.skin_type;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin');

DROP TABLE gwapese.skin_history;

DROP TABLE gwapese.skin;

COMMIT;
