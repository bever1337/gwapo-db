-- Revert gawpo-db:skin__weapon from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_weapon_description',
  'historical_skin_weapon_description');

DROP TABLE gwapese.historical_skin_weapon_description;

DROP TABLE gwapese.skin_weapon_description;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_weapon_flag',
  'historical_skin_weapon_flag');

DROP TABLE gwapese.historical_skin_weapon_flag;

DROP TABLE gwapese.skin_weapon_flag;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_weapon_name',
  'historical_skin_weapon_name');

DROP TABLE gwapese.historical_skin_weapon_name;

DROP TABLE gwapese.skin_weapon_name;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_weapon_restriction',
  'historical_skin_weapon_restriction');

DROP TABLE gwapese.historical_skin_weapon_restriction;

DROP TABLE gwapese.skin_weapon_restriction;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_weapon',
  'historical_skin_weapon');

DROP TABLE gwapese.historical_skin_weapon;

DROP TABLE gwapese.skin_weapon;

COMMIT;
