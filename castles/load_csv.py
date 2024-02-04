import csv
import datetime
import enum
import io
import luigi
from psycopg import sql

import common


class UnimplementedEnum(enum.Enum):
    pass


class LoadCsvTask(luigi.Task):
    precopy_sql: None | sql.SQL = None
    copy_sql: None | sql.SQL = None
    postcopy_sql: None | sql.SQL = None

    table = luigi.EnumParameter(enum=UnimplementedEnum)

    def output(self):
        raise NotImplementedError("Task must define output")

    def requires(self):
        raise NotImplementedError("Task must define requires")

    def run(self):
        if self.postcopy_sql is None:
            raise NotImplementedError("Task must implement postcopy_sql attribute")
        if self.table is UnimplementedEnum:
            raise NotImplementedError("Task must implement table parameter")

        r_input_file: io.FileIO
        w_output_file: io.FileIO
        with (
            self.input().get(self.table.value).open("r") as r_input_file,
            self.output().open("w") as w_output_file,
            common.get_conn() as connection,
        ):
            csv_reader = csv.DictReader(f=r_input_file, dialect="unix")

            precopy_sql = (
                self.precopy_sql
                if self.precopy_sql is not None
                else sql.Composed(
                    [
                        sql.SQL(
                            """
CREATE TEMPORARY TABLE {temp_table_name} (
    LIKE gwapese.{table_name}
) ON COMMIT DROP;
"""
                        ).format(
                            table_name=sql.Identifier(self.table.value),
                            temp_table_name=sql.Identifier(
                                "_".join(["tempo", self.table.value])
                            ),
                        ),
                        sql.SQL(
                            """
ALTER TABLE {temp_table_name}
    DROP COLUMN IF EXISTS sysrange_lower,
    DROP COLUMN IF EXISTS sysrange_upper;
"""
                        ).format(
                            temp_table_name=sql.Identifier(
                                "_".join(["tempo", self.table.value])
                            )
                        ),
                    ]
                )
            )

            copy_sql = (
                self.copy_sql
                if self.copy_sql is not None
                else sql.SQL(
                    """
COPY {temp_table_name} ({fields}) FROM STDIN (FORMAT 'csv');
"""
                ).format(
                    fields=sql.SQL(",").join(
                        [
                            sql.Identifier(fieldname)
                            for fieldname in csv_reader.fieldnames
                        ]
                    ),
                    temp_table_name=sql.Identifier(
                        "_".join(["tempo", self.table.value])
                    ),
                )
            )

            with connection.cursor() as cursor:
                try:
                    cursor.execute(query="BEGIN")
                    cursor.execute(precopy_sql)
                    with cursor.copy(copy_sql) as copy:
                        copy.write(r_input_file.read())
                    cursor.execute(self.postcopy_sql)
                    cursor.execute(query="COMMIT")
                    connection.commit()
                    w_output_file.write("ok")

                except Exception as exception_instance:
                    cursor.execute(query="ROLLBACK")
                    raise exception_instance