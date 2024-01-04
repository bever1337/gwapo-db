import assert from "node:assert";
import { after, before, describe, test } from "node:test";
import type { PoolClient } from "pg";

import { pool } from "../lib/pool";

describe("Lang", () => {
  let client: PoolClient;

  before(async (rdy) => {
    client = await pool.connect();
  });

  after(() => {
    client.release();
  });

  test("TODO", async () => {
    const inputLang = ["en", "es", "de", "fr", "zh"];

    await Promise.all(
      inputLang.map((languageTag) =>
        client.query({
          text: `CALL gwapese.insert_language_tag ($1);`,
          values: [languageTag],
        })
      )
    );

    const expectAllLang = await client
      .query(`SELECT lang_tag FROM gwapese.lang;`)
      .then((queryResult) =>
        queryResult.rows.map((row: { lang_tag: string }) => row.lang_tag)
      );

    assert(
      inputLang.every((lang_tag) => expectAllLang.includes(lang_tag)),
      new Error("Table does not include inserted values")
    );

    await client.query({
      text: `CALL gwapese.delete_language_tag ($1)`,
      values: ["en"],
    });

    const expectAllButEnLang = await client
      .query(`SELECT lang_tag FROM gwapese.lang;`)
      .then((queryResult) =>
        queryResult.rows.map((row: { lang_tag: string }) => row.lang_tag)
      );

    assert(!expectAllButEnLang.includes("en"));

    const expectDeletedEnLang = await client
      .query(
        `SELECT end_date, lang_tag, sysrange_lower FROM gwapese.lang_historical;`
      )
      .then((queryResult) =>
        queryResult.rows.map((row: { lang_tag: string }) => row.lang_tag)
      );

    assert(expectDeletedEnLang.includes("en"));
  });
});
