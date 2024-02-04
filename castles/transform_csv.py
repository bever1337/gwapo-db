import csv
import json
import luigi


class TransformCsvTask(luigi.Task):
    def get_rows(self, entity) -> list[dict]:
        raise NotImplementedError

    def output(self):
        raise NotImplementedError

    def requires(self):
        raise NotImplementedError

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
