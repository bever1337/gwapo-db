import luigi
from os import path
from psycopg import sql


import common
import config


class LoadGuildCurrency(luigi.Task):
    def output(self):
        gwapo_config = config.gconfig()
        target_filename = "{timestamp:s}.txt".format(
            timestamp=gwapo_config.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
        )
        target_path = path.join(
            gwapo_config.output_dir,
            "load_guild_currency",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def run(self):
        with (
            common.get_conn() as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute(query="BEGIN")
            try:
                cursor.execute(
                    query=sql.SQL(
                        """
MERGE INTO gwapese.guild_currency USING (
  VALUES
    ('Aetherium'),
    ('Favor')
) AS source_guild_currency (guild_currency_id) ON
  gwapese.guild_currency.guild_currency_id = source_guild_currency.guild_currency_id
WHEN NOT MATCHED THEN
  INSERT (guild_currency_id) VALUES (source_guild_currency.guild_currency_id);
"""
                    )
                )
                cursor.execute(query="COMMIT")
                connection.commit()
                with self.output().open("w") as w_output_file:
                    w_output_file.write("ok")
            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                raise exception_instance
