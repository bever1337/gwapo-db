import { RateLimit } from "async-sema";

import "../lib/environment";
import { pool } from "../lib/pool";

async function main() {
  const rateLimit = RateLimit(7);

  const client = await pool.connect();

  const dyedMaterials: string[] = await client
    .query(`SELECT material FROM gwapese.dyed_materials;`)
    .then((queryResult) => queryResult.rows.map((row) => row.material));

  console.log("Got materials", dyedMaterials.length);

  const languageTags: string[] = await client
    .query(`SELECT lang_tag FROM gwapese.lang;`)
    .then((queryResult) => queryResult.rows.map((row) => row.lang_tag));

  console.log("Got languages", languageTags);

  const colorIds: number[] = await fetch(
    `https://api.guildwars2.com/v2/colors`
  ).then((response): Promise<any> => response.json());

  console.log("Got color IDs", colorIds.length);

  const colorsByLanguage: Record<string, any>[][] = [];
  for (let i = 0; i < languageTags.length; i += 1) {
    colorsByLanguage[i] ??= [];
    const languageTag = languageTags[i];
    for (let j = 0; j < colorIds.length; j += 200) {
      const batchIds = colorIds.slice(j, j + 200).join(",");
      await rateLimit();
      const batchResponse = await fetch(
        `https://api.guildwars2.com/v2/colors?ids=${batchIds}&lang=${languageTag}`
      ).then(
        (response): Promise<Record<string, any>[]> =>
          response.json() as Promise<any>
      );
      colorsByLanguage[i].push(...batchResponse);
    }
  }

  try {
    await client.query("BEGIN");

    for (let i = 0; i < languageTags.length; i += 1) {
      const languageTag = languageTags[i];
      const colors = colorsByLanguage[i];
      console.log(`\t${languageTag}: ${colors.length}`);
      for (let j = 0; j < colors.length; j += 1) {
        const color = colors[j];
        const {
          id,
          name,
          categories: [hue_category, material_category, rarity_category],
        } = color;

        if (languageTag === "en") {
          await client.query({
            name: "upsertColor",
            text: `CALL gwapese.upsert_color($1, $2, $3, $4);`,
            values: [
              id,
              hue_category ?? null,
              material_category ?? null,
              rarity_category ?? null,
            ],
          });

          for (const material of dyedMaterials) {
            // known bug, the `hydra` dye is missing a `fur` color
            if (material === "fur" && id === 1594) {
              color[material] = color["cloth"];
            }
            const {
              [material]: {
                rgb: [red, green, blue],
                hue,
                saturation,
                lightness,
                brightness,
                contrast,
              },
            } = color;
            await client.query({
              name: "upsertDetailedColor",
              text: `CALL gwapese.upsert_color_sample($1, $2, $3, $4, $5, $6, $7, $8, $9, $10);`,
              values: [
                id,
                blue,
                brightness,
                contrast,
                green,
                hue,
                lightness,
                material,
                red,
                saturation,
              ],
            });
          }
        }

        await client.query({
          name: "upsertNamedColor",
          text: `CALL gwapese.upsert_color_name($1, $2, $3)`,
          values: [id, name, languageTag],
        });
      }
    }

    await client.query("COMMIT");
  } catch (anyError) {
    await client.query("ROLLBACK");
    throw anyError;
  } finally {
    client?.release();
  }
}

main()
  .catch(console.error)
  .finally(() => {
    pool.end();
  });
