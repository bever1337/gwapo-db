import { RateLimit } from "async-sema";
import type { PoolClient } from "pg";

import "../lib/environment";
import { pool } from "../lib/pool";

enum Category {
  General,
  Competitive,
  Map,
  Keys,
  Dungeon,
  BlackLion,
}

interface Gw2Currency {
  id: number;
  name: string;
  description: string;
  order: number;
  icon: string;
}

const rateLimit = RateLimit(7);
const toFetch = (languageTag: string) =>
  rateLimit().then(() =>
    fetch(
      `https://api.guildwars2.com/v2/currencies?ids=all&lang=${languageTag}`
    )
  );
const toJson = (response: Response): Promise<any> => response.json();
const manyToJson = (responses: Response[]) =>
  Promise.all(responses.map(toJson));

async function main() {
  let client: PoolClient;

  try {
    client = await pool.connect();

    const languageTags: string[] = await client
      .query(`SELECT (language_tag) FROM gwapese.language_tags;`)
      .then((queryResult) => queryResult.rows.map((row) => row.language_tag));

    const currenciesResponses: Gw2Currency[][] = await Promise.all(
      languageTags.map(toFetch)
    ).then(manyToJson);

    try {
      await client.query("BEGIN");
      for (const [index, currenciesForLang] of currenciesResponses.entries()) {
        const languageTag = languageTags[index];
        for (const {
          id,
          description,
          icon,
          name,
          order,
        } of currenciesForLang) {
          if (languageTag === "en") {
            await client.query({
              name: "preparedUpsertCurrency",
              text: `CALL gwapese.upsert_currency ($1, $2, $3, $4, $5);`,
              values: [
                id,
                additionalCurrencyDoc[id]?.categories ?? [Category.General],
                additionalCurrencyDoc[id]?.deprecated ?? false,
                icon,
                order,
              ],
            });
          }
          await client.query({
            name: "preparedUpsertCurrencyDescription",
            text: `CALL gwapese.upsert_currency_description ($1, $2, $3);`,
            values: [id, description, languageTag],
          });
          await client.query({
            name: "preparedUpsertCurrencyName",
            text: `CALL gwapese.upsert_currency_name ($1, $2, $3);`,
            values: [id, name, languageTag],
          });
        }
      }
      await client.query("COMMIT");
    } catch (anyError) {
      await client.query("ROLLBACK");
      throw anyError;
    }
  } catch (anyError) {
    console.error(anyError);
    throw anyError;
  } finally {
    cleanup();
  }

  function cleanup() {
    client?.release();
    pool.end();
  }
}

main();

const additionalCurrencyDoc: Record<
  number,
  { categories: Category[]; deprecated?: boolean }
> = {
  1: {
    categories: [Category.General],
  },
  2: {
    categories: [Category.General],
  },
  3: {
    categories: [Category.General],
  },
  4: {
    categories: [Category.General, Category.BlackLion],
  },
  5: {
    categories: [Category.Dungeon],
    deprecated: true,
  },
  6: {
    categories: [Category.Dungeon],
    deprecated: true,
  },
  7: {
    categories: [Category.Dungeon],
  },
  9: {
    categories: [Category.Dungeon],
    deprecated: true,
  },
  10: {
    categories: [Category.Dungeon],
    deprecated: true,
  },
  11: {
    categories: [Category.Dungeon],
    deprecated: true,
  },
  12: {
    categories: [Category.Dungeon],
    deprecated: true,
  },
  13: {
    categories: [Category.Dungeon],
    deprecated: true,
  },
  14: {
    categories: [Category.Dungeon],
    deprecated: true,
  },
  15: {
    categories: [Category.Competitive],
  },
  16: {
    categories: [Category.General],
  },
  18: {
    categories: [Category.General, Category.BlackLion],
  },
  19: {
    categories: [Category.Map],
  },
  20: {
    categories: [Category.Map],
  },
  22: {
    categories: [Category.Map],
  },
  23: {
    categories: [Category.General],
  },
  24: {
    categories: [Category.Dungeon],
  },
  25: {
    categories: [Category.Map],
  },
  26: {
    categories: [Category.Competitive],
  },
  27: {
    categories: [Category.Map],
  },
  28: {
    categories: [Category.Map],
  },
  29: {
    categories: [Category.Map],
  },
  30: {
    categories: [Category.Competitive],
  },
  31: {
    categories: [Category.Competitive],
  },
  32: {
    categories: [Category.Map],
  },
  33: {
    categories: [Category.Competitive],
  },
  34: {
    categories: [Category.Map],
  },
  35: {
    categories: [Category.Map],
  },
  36: {
    categories: [Category.Competitive],
  },
  37: {
    categories: [Category.Keys],
  },
  38: {
    categories: [Category.Keys],
  },
  39: {
    categories: [Category.Dungeon],
    deprecated: true,
  },
  40: {
    categories: [Category.Keys],
  },
  41: {
    categories: [Category.Keys],
  },
  42: {
    categories: [Category.Keys],
  },
  43: {
    categories: [Category.Keys],
  },
  44: {
    categories: [Category.Keys],
  },
  45: {
    categories: [Category.Map],
  },
  46: {
    categories: [Category.Competitive],
  },
  47: {
    categories: [Category.Map],
  },
  49: {
    categories: [Category.Keys],
  },
  50: {
    categories: [Category.Map],
  },
  51: {
    categories: [Category.Keys],
  },
  52: {
    categories: [Category.Map],
    deprecated: true,
  },
  53: {
    categories: [Category.Map],
  },
  54: {
    categories: [Category.Keys],
  },
  55: {
    categories: [Category.Keys],
    deprecated: true,
  },
  56: {
    categories: [Category.Keys],
    deprecated: true,
  },
  57: {
    categories: [Category.Map],
  },
  58: {
    categories: [Category.Map],
  },
  59: {
    categories: [Category.Dungeon],
  },
  60: {
    categories: [Category.Map],
  },
  61: {
    categories: [Category.Map],
  },
  62: {
    categories: [Category.Map],
  },
  63: {
    categories: [Category.General],
  },
  64: {
    categories: [Category.Map],
  },
  65: {
    categories: [Category.Competitive],
  },
  66: {
    categories: [Category.Map],
  },
  67: {
    categories: [Category.Map],
  },
  68: {
    categories: [Category.Map],
  },
  69: {
    categories: [Category.Dungeon],
  },
  70: {
    categories: [Category.Map],
  },
  71: {
    categories: [Category.Keys],
  },
  72: {
    categories: [Category.Map],
  },
  73: {
    categories: [Category.Map],
  },
  74: {
    categories: [Category.General],
    deprecated: true,
  },
};
