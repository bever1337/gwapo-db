import datetime
import luigi


class gconfig(luigi.Config):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    output_dir = luigi.PathParameter(absolute=True, exists=True)
