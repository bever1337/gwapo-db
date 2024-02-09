-- Verify gwapo-db:emote on pg
BEGIN;

SELECT
  emote_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.emote
WHERE
  FALSE;

SELECT
  emote_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.emote_history
WHERE
  FALSE;

SELECT
  command,
  emote_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.emote_command
WHERE
  FALSE;

SELECT
  command,
  emote_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.emote_command_history
WHERE
  FALSE;

ROLLBACK;
