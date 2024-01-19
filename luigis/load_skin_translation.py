import datetime
import json
import luigi
from operator import itemgetter
from os import path

import common
import load_lang
import load_skin
import transform_skin


class LoadSkinTranslation(luigi.Task):
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
            "load_skin_translation",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self) -> dict[common.LangTag, luigi.Task]:
        return {
            self.original_lang_tag.value: transform_skin.TransformSkin(
                extract_datetime=self.extract_datetime,
                lang_tag=self.original_lang_tag,
            ),
            self.translation_lang_tag.value: transform_skin.TransformSkin(
                extract_datetime=self.extract_datetime,
                lang_tag=self.translation_lang_tag,
            ),
            "_": load_skin.LoadSkin(
                extract_datetime=self.extract_datetime,
                lang_tag=self.original_lang_tag,
            ),
        }

    def run(self):
        if self.original_lang_tag.value == self.translation_lang_tag.value:
            raise RuntimeError("Cant translate self")

        inputs: dict[str, luigi.target.FileSystemTarget] = self.input()

        operating_skin_target = inputs[self.original_lang_tag.value]
        with operating_skin_target.open("r") as operating_skin_file:
            operating_skin_json = json.load(fp=operating_skin_file)

        translated_skin_target = inputs[self.translation_lang_tag.value]
        with translated_skin_target.open("r") as translated_skin_file:
            translated_skin_json = json.load(fp=translated_skin_file)

        if len(operating_skin_json) != len(translated_skin_json):
            raise RuntimeError("skin inputs are different length")

        operating_skin_sorted = sorted(operating_skin_json, key=itemgetter("id"))
        translated_skin_sorted = sorted(translated_skin_json, key=itemgetter("id"))

        for operating_skin, translated_skin in zip(
            operating_skin_sorted, translated_skin_sorted
        ):
            if operating_skin["id"] != translated_skin["id"]:
                raise RuntimeError("skin inputs do not match")

        with (
            common.get_conn() as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute(query="BEGIN")
            try:
                for operating_skin, translated_skin in zip(
                    operating_skin_sorted, translated_skin_sorted
                ):
                    if (
                        operating_skin["description"] != None
                        and translated_skin["description"] != None
                    ):
                        cursor.execute(
                            **load_lang.upsert_translated_copy(
                                app_name="gw2",
                                original_lang_tag=self.original_lang_tag.value,
                                original=operating_skin["description"],
                                translation_lang_tag=self.translation_lang_tag.value,
                                translation=translated_skin["description"],
                            )
                        )

                    if (
                        operating_skin["name"] != None
                        and translated_skin["name"] != None
                    ):
                        cursor.execute(
                            **load_lang.upsert_translated_copy(
                                app_name="gw2",
                                original_lang_tag=self.original_lang_tag.value,
                                original=operating_skin["name"],
                                translation_lang_tag=self.translation_lang_tag.value,
                                translation=translated_skin["name"],
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
