import luigi

import common


class LoadCsvTask(luigi.Task):
    precopy_sql = luigi.Parameter()
    copy_sql = luigi.Parameter()
    postcopy_sql = luigi.Parameter()

    def output(self):
        raise NotImplementedError

    def requires(self):
        raise NotImplementedError

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
