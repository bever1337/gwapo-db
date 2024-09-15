-- Revert gwapo-db:item from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'item_item_flag');

DROP TABLE gwapese.item_item_flag_history;

DROP TABLE gwapese.item_item_flag;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'item_item_game_type');

DROP TABLE gwapese.item_item_game_type_history;

DROP TABLE gwapese.item_item_game_type;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'item_restriction_profession');

DROP TABLE gwapese.item_restriction_profession_history;

DROP TABLE gwapese.item_restriction_profession;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'item_restriction_race');

DROP TABLE gwapese.item_restriction_race_history;

DROP TABLE gwapese.item_restriction_race;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'item_upgrade');

DROP TABLE gwapese.item_upgrade_history;

DROP TABLE gwapese.item_upgrade;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'item');

DROP TABLE gwapese.item_history;

DROP TABLE gwapese.item;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'item_flag');

DROP TABLE gwapese.item_flag_history;

DROP TABLE gwapese.item_flag;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'item_game_type');

DROP TABLE gwapese.item_game_type_history;

DROP TABLE gwapese.item_game_type;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'item_rarity');

DROP TABLE gwapese.item_rarity_history;

DROP TABLE gwapese.item_rarity;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'item_type');

DROP TABLE gwapese.item_type_history;

DROP TABLE gwapese.item_type;

COMMIT;
