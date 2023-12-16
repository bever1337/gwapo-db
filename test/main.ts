import process from "node:process";
import { finished } from "node:stream";
import { run } from "node:test";
import { tap } from "node:test/reporters";

import "../lib/environment";
import { pool } from "../lib/pool";

function main() {
  const stream = run({
    files: [
      "dist/test/currencies.test.js",
      "dist/test/lang.test.js",
      "dist/test/schema.test.js",
    ],
    concurrency: false,
    setup() {},
  }).compose(tap);

  finished(stream, function onFinished() {
    pool.end();
  });

  stream.pipe(process.stdout);
}

main();
