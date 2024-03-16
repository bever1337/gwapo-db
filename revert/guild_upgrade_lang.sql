-- Revert gwapo-db:guild_upgrade_lang from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'guild_upgrade_description_context');

DROP TABLE gwapese.guild_upgrade_description_context_history;

DROP TABLE gwapese.guild_upgrade_description_context;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'guild_upgrade_description');

DROP TABLE gwapese.guild_upgrade_description_history;

DROP TABLE gwapese.guild_upgrade_description;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'guild_upgrade_name_context');

DROP TABLE gwapese.guild_upgrade_name_context_history;

DROP TABLE gwapese.guild_upgrade_name_context;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'guild_upgrade_name');

DROP TABLE gwapese.guild_upgrade_name_history;

DROP TABLE gwapese.guild_upgrade_name;

COMMIT;
