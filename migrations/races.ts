import { PoolClient } from "pg";

import "../lib/environment";
import { pool } from "../lib/pool";

function main() {
  return Promise.all([
    pool.connect(),
    fetch(`https://api.guildwars2.com/v2/races`).then(
      (response): Promise<string[]> => response.json() as Promise<any>
    ),
  ]).then(([client, races]: [PoolClient, string[]]) =>
    client
      .query("BEGIN")
      .then(() =>
        Promise.all(
          races.map((race) =>
            client.query({
              text: `CALL gwapese.upsert_race ($1);`,
              values: [race],
            })
          )
        )
      )
      .then(() => client.query("COMMIT"))
      .catch(async (error) => {
        await client.query("ROLLBACK");
        throw error;
      })
      .finally(() => {
        client?.release();
        pool.end();
      })
  );
}

main();
