import datetime
import json
import luigi
from os import path

import common
import transform_skin_type


class LoadSkinBack(luigi.Task):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)

    def output(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.txt".format(
            lang_tag=self.lang_tag.value,
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
        )
        target_path = path.join(
            self.output_dir,
            "load_skin_back",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        return transform_skin_type.TransformSkinType(
            extract_datetime=self.extract_datetime,
            lang_tag=self.lang_tag,
            skin_type=common.SkinType.Back,
        )

    def run(self):
        with (
            self.input().open("r") as r_input_file,
            common.get_conn() as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute(query="BEGIN")
            try:
                for skin_line in r_input_file:
                    skin = json.loads(skin_line)
                    cursor.execute(**upsert_skin_back(skin_id=skin["id"]))

                cursor.execute(query="COMMIT")
                connection.commit()
                with self.output().open("w") as w_output:
                    w_output.write("ok")

            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                raise exception_instance


def upsert_skin_back(skin_id: int) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.skin_back AS target_skin_back
USING (
  VALUES (%(skin_id)s::integer)
) AS source_skin_back (skin_id)
ON
  target_skin_back.skin_id = source_skin_back.skin_id
WHEN NOT MATCHED THEN
  INSERT (skin_id)
    VALUES (source_skin_back.skin_id);
""",
        "params": {"skin_id": skin_id},
    }
