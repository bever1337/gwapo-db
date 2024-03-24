-- Revert gwapo-db:guild_upgrade from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'guild_upgrade_prerequisite');

DROP TABLE gwapese.guild_upgrade_prerequisite_history;

DROP TABLE gwapese.guild_upgrade_prerequisite;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'guild_upgrade');

DROP TABLE gwapese.guild_upgrade_history;

DROP TABLE gwapese.guild_upgrade;

COMMIT;
