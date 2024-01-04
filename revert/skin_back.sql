-- Revert gawpo-db:skin__back from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_back_description',
  'historical_skin_back_description');

DROP TABLE gwapese.historical_skin_back_description;

DROP TABLE gwapese.skin_back_description;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_back_flag',
  'historical_skin_back_flag');

DROP TABLE gwapese.historical_skin_back_flag;

DROP TABLE gwapese.skin_back_flag;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_back_name',
  'historical_skin_back_name');

DROP TABLE gwapese.historical_skin_back_name;

DROP TABLE gwapese.skin_back_name;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_back_restriction',
  'historical_skin_back_restriction');

DROP TABLE gwapese.historical_skin_back_restriction;

DROP TABLE gwapese.skin_back_restriction;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_back',
  'historical_skin_back');

DROP TABLE gwapese.historical_skin_back;

DROP TABLE gwapese.skin_back;

COMMIT;
