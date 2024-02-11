import csv
import datetime
import json
import luigi
from os import path

import config


class TransformCsvTask(luigi.Task):
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())

    def get_rows(self, entity) -> list[dict]:
        raise NotImplementedError()

    def output(self):
        gwapo_config = config.gconfig()
        return luigi.LocalTarget(
            path=path.join(
                gwapo_config.output_dir,
                self.get_task_family(),
                path.extsep.join([self.task_id, "csv"]),
            )
        )

    def requires(self):
        raise NotImplementedError()

    def run(self):
        with (
            self.input().open("r") as r_input_file,
            self.output().open("w") as w_output_file,
        ):
            csv_writer = None
            for entity_line in r_input_file:
                entity = json.loads(entity_line)

                rows = self.get_rows(entity)

                if len(rows) == 0:
                    continue

                if csv_writer is None:
                    fieldnames = rows[0].keys()
                    csv_writer = csv.DictWriter(
                        f=w_output_file, dialect="unix", fieldnames=fieldnames
                    )
                    csv_writer.writeheader()
                csv_writer.writerows(rows)
            if csv_writer is None:
                raise RuntimeError("Wrote 0 rows")
