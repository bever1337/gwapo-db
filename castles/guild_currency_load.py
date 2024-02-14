import datetime

import luigi
from os import path
from psycopg import sql

import common
from tasks import config


class GuildCurrencyLoad(luigi.Task):
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    task_namespace = "guild_currency"

    def output(self):
        gwapo_config = config.gconfig()
        return luigi.LocalTarget(
            path=path.join(
                gwapo_config.output_dir,
                self.get_task_family(),
                path.extsep.join([self.task_id, "txt"]),
            )
        )

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
