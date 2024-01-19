import datetime
import json
import luigi
from operator import itemgetter
from os import path

import common
import load_currency
import load_lang
import transform_currency


class LoadCurrencyTranslation(luigi.Task):
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
            "load_currency_translation",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self) -> dict[common.LangTag, luigi.Task]:
        return {
            self.original_lang_tag.value: transform_currency.TransformCurrency(
                extract_datetime=self.extract_datetime,
                lang_tag=self.original_lang_tag,
            ),
            self.translation_lang_tag.value: transform_currency.TransformCurrency(
                extract_datetime=self.extract_datetime,
                lang_tag=self.translation_lang_tag,
            ),
            "_": load_currency.LoadCurrency(
                extract_datetime=self.extract_datetime,
                lang_tag=self.original_lang_tag,
            ),
        }

    def run(self):
        if self.original_lang_tag.value == self.translation_lang_tag.value:
            raise RuntimeError("Cant translate self")

        inputs: dict[str, luigi.target.FileSystemTarget] = self.input()

        operating_currency_target = inputs[self.original_lang_tag.value]
        with operating_currency_target.open("r") as operating_currency_file:
            operating_currency_json = json.load(fp=operating_currency_file)

        translated_currency_target = inputs[self.translation_lang_tag.value]
        with translated_currency_target.open("r") as translated_currency_file:
            translated_currency_json = json.load(fp=translated_currency_file)

        if len(operating_currency_json) != len(translated_currency_json):
            raise RuntimeError("currency inputs do not match")

        operating_currency_sorted = sorted(
            operating_currency_json, key=itemgetter("id")
        )
        translated_currency_sorted = sorted(
            translated_currency_json, key=itemgetter("id")
        )

        for operating_currency, translated_currency in zip(
            operating_currency_sorted, translated_currency_sorted
        ):
            if operating_currency["id"] != translated_currency["id"]:
                raise RuntimeError("currency inputs do not match")

        with (
            common.get_conn() as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute(query="BEGIN")
            try:
                for operating_currency, translated_currency in zip(
                    operating_currency_sorted, translated_currency_sorted
                ):
                    cursor.execute(
                        **load_lang.upsert_translated_copy(
                            app_name="gw2",
                            original_lang_tag=self.original_lang_tag.value,
                            original=operating_currency["description"],
                            translation_lang_tag=self.translation_lang_tag.value,
                            translation=translated_currency["description"],
                        )
                    )
                    cursor.execute(
                        **load_lang.upsert_translated_copy(
                            app_name="gw2",
                            original_lang_tag=self.original_lang_tag.value,
                            original=operating_currency["name"],
                            translation_lang_tag=self.translation_lang_tag.value,
                            translation=translated_currency["name"],
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
