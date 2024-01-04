import "../lib/environment";
import { pool } from "../lib/pool";

const known_lang = ["en", "es", "de", "fr", "zh"];
const gw2_app = ["gw2"];
const gw2_operating_lang = [gw2_app[0], known_lang[0]];

const main = () =>
  pool.connect().then((client) =>
    client
      .query("BEGIN")
      .then(() =>
        client.query({
          text: `\
MERGE INTO gwapese.lang AS old_lang
USING (
  VALUES ($1), ($2), ($3), ($4), ($5)
) AS new_lang (lang_tag)
ON
  old_lang.lang_tag = new_lang.lang_tag
WHEN NOT MATCHED THEN
  INSERT (lang_tag)
  VALUES (new_lang.lang_tag);`,
          values: known_lang,
        })
      )
      .then(() =>
        client.query({
          text: `\
MERGE INTO gwapese.app AS old_app
USING (
  VALUES ($1)
) AS new_app (app_name)
ON
  old_app.app_name = new_app.app_name
WHEN NOT MATCHED THEN
  INSERT (app_name)
  VALUES (new_app.app_name);`,
          values: gw2_app,
        })
      )
      .then(() =>
        client.query({
          text: `\
MERGE INTO gwapese.operating_lang AS old_operating_lang
USING (
  VALUES ($1, $2)
) AS new_operating_lang (app_name, lang_tag)
ON
  old_operating_lang.app_name = new_operating_lang.app_name
  AND old_operating_lang.lang_tag = new_operating_lang.lang_tag
WHEN NOT MATCHED THEN
  INSERT (app_name, lang_tag)
  VALUES (new_operating_lang.app_name, new_operating_lang.lang_tag);`,
          values: gw2_operating_lang,
        })
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

main().catch(console.error);
