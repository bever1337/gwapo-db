import datetime
import json
import luigi
from operator import itemgetter
from os import path

import common
import load_color
import load_lang
import transform_color


class LoadColorTranslation(luigi.Task):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    original_lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)
    translation_lang_tag = luigi.EnumParameter(enum=common.LangTag)

    def output(self):
        target_filename = "{timestamp:s}__original_{original_lang_tag:s}__translation_{translation_lang_tag:s}.txt".format(
            original_lang_tag=self.original_lang_tag.value,
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            translation_lang_tag=self.translation_lang_tag.value,
        )
        target_path = path.join(
            self.output_dir,
            "load_color_translation",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self) -> dict[common.LangTag, luigi.Task]:
        return {
            self.original_lang_tag.value: transform_color.TransformColor(
                extract_datetime=self.extract_datetime,
                lang_tag=self.original_lang_tag,
            ),
            self.translation_lang_tag.value: transform_color.TransformColor(
                extract_datetime=self.extract_datetime,
                lang_tag=self.translation_lang_tag,
            ),
            "_": load_color.LoadColor(
                extract_datetime=self.extract_datetime,
                lang_tag=self.original_lang_tag,
            ),
        }

    def run(self):
        if self.original_lang_tag.value == self.translation_lang_tag.value:
            raise RuntimeError("Cant translate self")

        inputs: dict[str, luigi.target.FileSystemTarget] = self.input()

        operating_color_target = inputs[self.original_lang_tag.value]
        with operating_color_target.open("r") as operating_color_file:
            operating_color_json = json.load(fp=operating_color_file)

        translated_color_target = inputs[self.translation_lang_tag.value]
        with translated_color_target.open("r") as translated_color_file:
            translated_color_json = json.load(fp=translated_color_file)

        if len(operating_color_json) != len(translated_color_json):
            raise RuntimeError("currency inputs do not match")

        operating_color_sorted = sorted(operating_color_json, key=itemgetter("id"))
        translated_color_sorted = sorted(translated_color_json, key=itemgetter("id"))

        for operating_color, translated_color in zip(
            operating_color_sorted, translated_color_sorted
        ):
            if operating_color["id"] != translated_color["id"]:
                raise RuntimeError("color inputs do not match")

        with (
            common.get_conn() as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute(query="BEGIN")
            try:
                for operating_color, translated_color in zip(
                    operating_color_sorted, translated_color_sorted
                ):
                    cursor.execute(
                        **load_lang.upsert_translated_copy(
                            app_name="gw2",
                            original_lang_tag=self.original_lang_tag.value,
                            original=operating_color["name"],
                            translation_lang_tag=self.translation_lang_tag.value,
                            translation=translated_color["name"],
                        )
                    )

                cursor.execute(query="COMMIT")
                connection.commit()
                with self.output().open("w") as w_output:
                    w_output.write("ok")

            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                connection.rollback()
                raise exception_instance
