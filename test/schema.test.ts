import assert from "node:assert";
import { after, before, describe, test } from "node:test";
import type { PoolClient } from "pg";

import { pool } from "../lib/pool";

describe("Schema", () => {
  let client: PoolClient;

  before(async (rdy) => {
    client = await pool.connect();
  });

  after(() => {
    client.release();
  });

  test("TODO", () => {
    // This test passes because it does not throw an exception.
    assert.strictEqual(1, 1);
  });
});
