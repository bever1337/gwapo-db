-- Verify gwapo-db:item on pg
BEGIN;

SELECT
  chat_link,
  icon,
  item_id,
  rarity,
  required_level,
  sysrange_lower,
  sysrange_upper,
  vendor_value
FROM
  gwapese.item
WHERE
  FALSE;

SELECT
  chat_link,
  icon,
  item_id,
  rarity,
  required_level,
  sysrange_lower,
  sysrange_upper,
  vendor_value
FROM
  gwapese.item_history
WHERE
  FALSE;

SELECT
  app_name,
  item_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.item_description
WHERE
  FALSE;

SELECT
  app_name,
  item_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.item_description_history
WHERE
  FALSE;

SELECT
  flag,
  item_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.item_flag
WHERE
  FALSE;

SELECT
  flag,
  item_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.item_flag_history
WHERE
  FALSE;

SELECT
  game_type,
  item_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.item_game_type
WHERE
  FALSE;

SELECT
  game_type,
  item_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.item_game_type_history
WHERE
  FALSE;

SELECT
  app_name,
  item_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.item_name
WHERE
  FALSE;

SELECT
  app_name,
  item_id,
  lang_tag,
  original,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.item_name_history
WHERE
  FALSE;

SELECT
  item_id,
  profession_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.item_profession_restriction
WHERE
  FALSE;

SELECT
  item_id,
  profession_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.item_profession_restriction_history
WHERE
  FALSE;

SELECT
  item_id,
  race_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.item_race_restriction
WHERE
  FALSE;

SELECT
  item_id,
  race_id,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.item_race_restriction_history
WHERE
  FALSE;

SELECT
  item_id,
  item_type,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.item_type
WHERE
  FALSE;

SELECT
  item_id,
  item_type,
  sysrange_lower,
  sysrange_upper
FROM
  gwapese.item_type_history
WHERE
  FALSE;

SELECT
  from_item_id,
  sysrange_lower,
  sysrange_upper,
  to_item_id,
  upgrade
FROM
  gwapese.item_upgrade
WHERE
  FALSE;

SELECT
  from_item_id,
  sysrange_lower,
  sysrange_upper,
  to_item_id,
  upgrade
FROM
  gwapese.item_upgrade_history
WHERE
  FALSE;

ROLLBACK;
