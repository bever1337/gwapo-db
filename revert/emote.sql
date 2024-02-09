-- Revert gwapo-db:emote from pg
BEGIN;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'emote_command');

DROP TABLE gwapese.emote_command_history;

DROP TABLE gwapese.emote_command;

CALL temporal_tables.drop_historicize_fn ('gwapese', 'emote');

DROP TABLE gwapese.emote_history;

DROP TABLE gwapese.emote;

COMMIT;
