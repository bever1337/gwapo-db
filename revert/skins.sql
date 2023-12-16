-- Revert gawpo-db:skins from pg
BEGIN;

DROP PROCEDURE gwapese.upsert_armor_skin;

DROP PROCEDURE gwapese.upsert_back_skin;

DROP PROCEDURE gwapese.upsert_described_skin;

DROP PROCEDURE gwapese.upsert_dyed_skin_slot;

DROP PROCEDURE gwapese.upsert_gathering_skin;

DROP PROCEDURE gwapese.upsert_named_skin;

DROP PROCEDURE gwapese.upsert_weapon_skin;

DROP PROCEDURE gwapese.upsert_skin;

DROP TABLE gwapese.dyed_skin_slots;

DROP TABLE gwapese.armor_skins;

DROP TABLE gwapese.back_skins;

DROP TABLE gwapese.described_skins;

DROP TABLE gwapese.flagged_skins;

DROP TABLE gwapese.gathering_skins;

DROP TABLE gwapese.named_skins;

DROP TABLE gwapese.restricted_skins;

DROP TABLE gwapese.weapon_skins;

DROP TABLE gwapese.skins;

DROP TABLE gwapese.skin_flags;

DROP TABLE gwapese.skin_types;

COMMIT;
