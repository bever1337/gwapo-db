-- Revert gwapo-db:skins from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_armor_dye_slot');

DROP TABLE gwapese.skin_armor_dye_slot_history;

DROP TABLE gwapese.skin_armor_dye_slot;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_armor');

DROP TABLE gwapese.skin_armor_history;

DROP TABLE gwapese.skin_armor;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_back');

DROP TABLE gwapese.skin_back_history;

DROP TABLE gwapese.skin_back;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_gathering');

DROP TABLE gwapese.skin_gathering_history;

DROP TABLE gwapese.skin_gathering;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'skin_weapon');

DROP TABLE gwapese.skin_weapon_history;

DROP TABLE gwapese.skin_weapon;

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
