-- Revert gawpo-db:skin_gathering from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_gathering_description',
  'historical_skin_gathering_description');

DROP TABLE gwapese.historical_skin_gathering_description;

DROP TABLE gwapese.skin_gathering_description;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_gathering_flag',
  'historical_skin_gathering_flag');

DROP TABLE gwapese.historical_skin_gathering_flag;

DROP TABLE gwapese.skin_gathering_flag;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_gathering_name',
  'historical_skin_gathering_name');

DROP TABLE gwapese.historical_skin_gathering_name;

DROP TABLE gwapese.skin_gathering_name;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_gathering_restriction',
  'historical_skin_gathering_restriction');

DROP TABLE gwapese.historical_skin_gathering_restriction;

DROP TABLE gwapese.skin_gathering_restriction;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_gathering',
  'historical_skin_gathering');

DROP TABLE gwapese.historical_skin_gathering;

DROP TABLE gwapese.skin_gathering;

COMMIT;
