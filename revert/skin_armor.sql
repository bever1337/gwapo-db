-- Revert gawpo-db:skin__armor from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_armor_description',
  'historical_skin_armor_description');

DROP TABLE gwapese.historical_skin_armor_description;

DROP TABLE gwapese.skin_armor_description;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_armor_dye_slot',
  'historical_skin_armor_dye_slot');

DROP TABLE gwapese.historical_skin_armor_dye_slot;

DROP TABLE gwapese.skin_armor_dye_slot;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_armor_flag',
  'historical_skin_armor_flag');

DROP TABLE gwapese.historical_skin_armor_flag;

DROP TABLE gwapese.skin_armor_flag;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_armor_name',
  'historical_skin_armor_name');

DROP TABLE gwapese.historical_skin_armor_name;

DROP TABLE gwapese.skin_armor_name;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_armor_restriction',
  'historical_skin_armor_restriction');

DROP TABLE gwapese.historical_skin_armor_restriction;

DROP TABLE gwapese.skin_armor_restriction;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_armor',
  'historical_skin_armor');

DROP TABLE gwapese.historical_skin_armor;

DROP TABLE gwapese.skin_armor;

COMMIT;
