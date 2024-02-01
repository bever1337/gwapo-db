import luigi
from psycopg import sql

import common


create_temporary_table = sql.SQL(
    """
CREATE TEMPORARY TABLE {temp_table_name} (
    LIKE gwapese.{table_name}
) ON COMMIT DROP;
ALTER TABLE {temp_table_name}
    DROP COLUMN IF EXISTS sysrange_lower,
    DROP COLUMN IF EXISTS sysrange_upper;
"""
)

copy_from_stdin = sql.SQL(
    """
COPY {temp_table_name} FROM STDIN (FORMAT 'csv', HEADER);
"""
)


class LoadCsvTask(luigi.Task):
    precopy_sql: None | sql.SQL = None
    copy_sql: None | sql.SQL = None
    postcopy_sql: None | sql.SQL = None

    def output(self):
        raise NotImplementedError()

    def requires(self):
        raise NotImplementedError()

    def run(self):
        with (
            self.input().open("r") as r_input_file,
            self.output().open("w") as w_output,
            common.get_conn() as connection,
        ):
            with connection.cursor() as cursor:
                try:
                    cursor.execute(query="BEGIN")
                    cursor.execute(self.precopy_sql)
                    with cursor.copy(self.copy_sql) as copy:
                        copy.write(r_input_file.read())
                    cursor.execute(self.postcopy_sql)
                    cursor.execute(query="COMMIT")
                    connection.commit()
                    w_output.write("ok")

                except Exception as exception_instance:
                    cursor.execute(query="ROLLBACK")
                    raise exception_instance
