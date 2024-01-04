-- Revert gawpo-db:skins from pg
BEGIN;

DROP TABLE gwapese.historical_skin_description;

DROP TABLE gwapese.skin_description;

DROP TABLE gwapese.historical_skin_flag;

DROP TABLE gwapese.skin_flag;

DROP TABLE gwapese.historical_skin_name;

DROP TABLE gwapese.skin_name;

DROP TABLE gwapese.historical_skin_restriction;

DROP TABLE gwapese.skin_restriction;

DROP TABLE gwapese.historical_armor_skin_dye_slot;

DROP TABLE gwapese.armor_skin_dye_slot;

DROP TABLE gwapese.historical_armor_skin;

DROP TABLE gwapese.armor_skin;

DROP TABLE gwapese.historical_back_skin;

DROP TABLE gwapese.back_skin;

DROP TABLE gwapese.historical_gathering_skin;

DROP TABLE gwapese.gathering_skin;

DROP TABLE gwapese.historical_weapon_skin;

DROP TABLE gwapese.weapon_skin;

DROP TABLE gwapese.historical_skin;

DROP TABLE gwapese.skin;

COMMIT;
