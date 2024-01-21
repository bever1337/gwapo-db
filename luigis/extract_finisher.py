import datetime
import luigi
from os import path

import common
import extract_batch


class ExtractFinisher(luigi.WrapperTask):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)

    def requires(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.json".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        yield extract_batch.ExtractBatch(
            entity_schema="../schema/gw2/v2/finishers/finisher.json",
            extract_datetime=self.extract_datetime,
            extract_dir=path.join(self.output_dir, "extract_finisher_id"),
            id_schema="../schema/gw2/v2/finishers/index.json",
            output_file=path.join(
                self.output_dir,
                "extract_finisher",
                target_filename,
            ),
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/finishers",
        )
