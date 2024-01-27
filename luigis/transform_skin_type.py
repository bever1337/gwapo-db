import datetime
import json
import luigi
from os import path

import common
import transform_skin


class TransformSkinType(luigi.Task):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)
    skin_type = luigi.EnumParameter(enum=common.SkinType)

    def output(self):
        target_filename = (
            "{timestamp:s}__lang_{lang_tag:s}__type_{skin_type:s}.ndjson".format(
                timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
                lang_tag=self.lang_tag.value,
                skin_type=self.skin_type.value,
            )
        )
        target_path = path.join(
            self.output_dir,
            "transform_skin_type",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        return transform_skin.TransformSkin(
            extract_datetime=self.extract_datetime, lang_tag=self.lang_tag
        )

    def run(self):
        with (
            self.input().open("r") as r_input_file,
            self.output().open("w") as w_output,
        ):
            skin_type = self.skin_type.value

            for skin_line in r_input_file:
                skin = json.loads(skin_line)
                if skin["type"] == skin_type:
                    w_output.write(skin_line)
