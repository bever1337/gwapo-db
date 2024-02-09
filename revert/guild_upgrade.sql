-- Revert gwapo-db:guild_upgrade from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'guild_upgrade_prerequisite');

DROP TABLE gwapese.guild_upgrade_prerequisite_history;

DROP TABLE gwapese.guild_upgrade_prerequisite;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'guild_upgrade_description');

DROP TABLE gwapese.guild_upgrade_description_history;

DROP TABLE gwapese.guild_upgrade_description;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'guild_upgrade_name');

DROP TABLE gwapese.guild_upgrade_name_history;

DROP TABLE gwapese.guild_upgrade_name;

-- CALL temporal_tables.drop_historicize_fn ('gwapese', 'guild_upgrade_unlock');
-- DROP TABLE gwapese.guild_upgrade_unlock_history;
-- DROP TABLE gwapese.guild_upgrade_unlock;
CALL temporal_tables.drop_historicize_fn ('gwapese', 'guild_upgrade');

DROP TABLE gwapese.guild_upgrade_history;

DROP TABLE gwapese.guild_upgrade;

COMMIT;
