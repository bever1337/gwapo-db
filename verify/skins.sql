-- Verify gawpo-db:skins on pg
BEGIN;

SELECT
  skin_flag
FROM
  gwapese.skin_flags
WHERE
  FALSE;

SELECT
  skin_type
FROM
  gwapese.skin_types
WHERE
  FALSE;

SELECT
  id,
  icon,
  rarity,
  skin_type
FROM
  gwapese.skins
WHERE
  FALSE;

SELECT
  id,
  skin_type,
  slot,
  weight_class
FROM
  gwapese.armor_skins
WHERE
  FALSE;

SELECT
  id,
  skin_type
FROM
  gwapese.back_skins
WHERE
  FALSE;

SELECT
  id,
  language_tag,
  skin_description
FROM
  gwapese.described_skins
WHERE
  FALSE;

SELECT
  id,
  slot_index,
  color,
  material
FROM
  gwapese.dyed_skin_slots
WHERE
  FALSE;

SELECT
  id,
  slot_index,
  color,
  material
FROM
  gwapese.dyed_skin_slots
WHERE
  FALSE;

SELECT
  id,
  skin_flag
FROM
  gwapese.flagged_skins
WHERE
  FALSE;

SELECT
  id,
  skin_type,
  tool
FROM
  gwapese.gathering_skins
WHERE
  FALSE;

SELECT
  id,
  language_tag,
  skin_name
FROM
  gwapese.named_skins
WHERE
  FALSE;

SELECT
  id,
  restriction
FROM
  gwapese.restricted_skins
WHERE
  FALSE;

SELECT
  id,
  damage_type,
  skin_type,
  weapon_type
FROM
  gwapese.weapon_skins
WHERE
  FALSE;

SELECT
  HAS_FUNCTION_PRIVILEGE('gwapese.upsert_skin(smallint, text, text, text)', 'execute');

SELECT
  HAS_FUNCTION_PRIVILEGE('gwapese.upsert_armor_skin(smallint, text, text, text, text)', 'execute');

SELECT
  HAS_FUNCTION_PRIVILEGE('gwapese.upsert_back_skin(smallint, text, text)', 'execute');

SELECT
  HAS_FUNCTION_PRIVILEGE('gwapese.upsert_described_skin(smallint, text, text)', 'execute');

SELECT
  HAS_FUNCTION_PRIVILEGE('gwapese.upsert_dyed_skin_slot(smallint, smallint, text, smallint)', 'execute');

SELECT
  HAS_FUNCTION_PRIVILEGE('gwapese.upsert_gathering_skin(smallint, text, text, text)', 'execute');

SELECT
  HAS_FUNCTION_PRIVILEGE('gwapese.upsert_named_skin(smallint, text, text)', 'execute');

SELECT
  HAS_FUNCTION_PRIVILEGE('gwapese.upsert_weapon_skin(smallint, text, text, text, text)', 'execute');

ROLLBACK;
