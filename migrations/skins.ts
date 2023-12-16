import { RateLimit } from "async-sema";

import "../lib/environment";
import { pool } from "../lib/pool";

async function main() {
  const rateLimit = RateLimit(7);

  const client = await pool.connect();

  const languageTags: string[] = await client
    .query(`SELECT (language_tag) FROM gwapese.language_tags;`)
    .then((queryResult) => queryResult.rows.map((row) => row.language_tag));

  console.log("Got languages", languageTags);

  const skinIds: number[] = await fetch(
    `https://api.guildwars2.com/v2/skins`
  ).then((response): Promise<any> => response.json());

  console.log("Got skin IDs", skinIds.length);

  const skinsByLanguage: Record<string, any>[][] = [];
  for (let i = 0; i < languageTags.length; i += 1) {
    skinsByLanguage[i] ??= [];
    const languageTag = languageTags[i];
    for (let j = 0; j < skinIds.length; j += 200) {
      const batchIds = skinIds.slice(j, j + 200).join(",");
      await rateLimit();
      const batchResponse = await fetch(
        `https://api.guildwars2.com/v2/skins?ids=${batchIds}&lang=${languageTag}`
      ).then(
        (response): Promise<Record<string, any>[]> =>
          response.json() as Promise<any>
      );
      skinsByLanguage[i].push(...batchResponse);
    }
  }

  try {
    await client.query("BEGIN");

    for (let i = 0; i < languageTags.length; i += 1) {
      const languageTag = languageTags[i];
      const skins = skinsByLanguage[i];
      console.log(`\t${languageTag}: ${skins.length}`);
      for (let j = 0; j < skins.length; j += 1) {
        const {
          description,
          details,
          flags,
          id,
          icon,
          name,
          rarity,
          restrictions,
          type: skinType,
        } = skins[j];

        if (languageTag === "en") {
          if (skinType === "Armor") {
            const { type: slot, weight_class } = details;
            await client.query({
              name: "upsertArmorSkins",
              text: `CALL gwapese.upsert_armor_skin ($1, $2, $3, $4, $5);`,
              values: [id, icon, rarity, slot, weight_class],
            });

            for (let dyeSlotIndex = 0; dyeSlotIndex < 4; dyeSlotIndex += 1) {
              const { color_id, material } = details?.dye_slots?.default?.[
                dyeSlotIndex
              ] ?? { color_id: null, material: null };
              await client.query({
                name: "upsertDyedSkinSlots",
                text: `CALL gwapese.upsert_dyed_skin_slot ($1, $2, $3, $4);`,
                values: [id, color_id, material, dyeSlotIndex],
              });
            }
          } else if (skinType === "Back") {
            await client.query({
              name: "upsertBackSkins",
              text: `CALL gwapese.upsert_back_skin ($1, $2, $3);`,
              values: [id, icon, rarity],
            });
          } else if (skinType === "Gathering") {
            const { type: tool } = details;
            await client.query({
              name: "upsertGatheringSkins",
              text: `CALL gwapese.upsert_gathering_skin ($1, $2, $3, $4);`,
              values: [id, icon, rarity, tool],
            });
          } else if (skinType === "Weapon") {
            const { type: weapon_type, damage_type } = details;
            await client.query({
              name: "upsertWeaponSkins",
              text: `CALL gwapese.upsert_weapon_skin ($1, $2, $3, $4, $5);`,
              values: [id, damage_type, icon, rarity, weapon_type],
            });
          } else {
            throw new Error(`Unexpected skin type: ${skinType}`);
          }

          // for (const flag of flags ?? []) {
          //   await client.query({
          //     name: "insertSkinFlags",
          //     text: `INSERT INTO gwapese.flagged_skins (id, skin_flag) VALUES ($1, $2)`,
          //     values: [id, flag],
          //   });
          // }

          // for (const restriction of restrictions ?? []) {
          //   await client.query({
          //     name: "insertSkinRestrictions",
          //     text: `INSERT INTO gwapese.restricted_skins (id, restriction) VALUES ($1, $2)`,
          //     values: [id, restriction],
          //   });
          // }
        }

        if (typeof description === "string" && description.length > 0) {
          await client.query({
            name: "upsertSkinDescriptions",
            text: `CALL gwapese.upsert_described_skin ($1, $2, $3);`,
            values: [id, languageTag, description],
          });
        }

        await client.query({
          name: "upsertSkinNames",
          text: `CALL gwapese.upsert_named_skin ($1, $2, $3)`,
          values: [id, languageTag, name],
        });
      }
    }

    await client.query("COMMIT");
  } catch (anyError) {
    console.error(anyError);
    await client.query("ROLLBACK");
    throw anyError;
  } finally {
    client?.release();
  }
}

main().finally(() => {
  pool.end();
});
