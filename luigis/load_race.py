import datetime
import json
import luigi
from os import path

import common
import extract_race


class LoadRace(luigi.Task):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)

    def output(self):
        target_filename = "{timestamp:s}.txt".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
        )
        target_path = path.join(
            self.output_dir,
            "load_race",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        return extract_race.ExtractRace(extract_datetime=self.extract_datetime)

    def run(self):
        with self.input().open("r") as ro_input_file:
            json_input = json.load(fp=ro_input_file)

        with (
            common.get_conn() as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute(query="BEGIN")
            try:
                for race_name in json_input:
                    cursor.execute(
                        query="""
                            MERGE INTO gwapese.race AS target_race
                            USING (VALUES (%s::text)) AS source_race (race_name)
                                ON target_race.race_name = source_race.race_name
                            WHEN NOT MATCHED THEN
                                INSERT (race_name)
                                    VALUES (source_race.race_name);
                            """,
                        params=(race_name,),
                    )

                cursor.execute(query="COMMIT")
                connection.commit()
                with self.output().open("w") as w_output:
                    w_output.write("ok")

            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                raise exception_instance
