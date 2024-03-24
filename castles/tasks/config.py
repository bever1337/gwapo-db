import datetime
import luigi


class gconfig(luigi.Config):
    output_dir = luigi.PathParameter(absolute=True, exists=True)
    task_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
