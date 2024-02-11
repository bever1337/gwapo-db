import luigi


class gconfig(luigi.Config):
    output_dir = luigi.PathParameter(absolute=True, exists=True)
