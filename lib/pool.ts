import { Pool } from "pg";

export const pool = new Pool({
  connectionTimeoutMillis: 4200,
});
