import datetime
import json
import luigi
from os import path

import common
import transform_skin_type


class LoadSkinGathering(luigi.Task):
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
            "load_skin_gathering",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        return transform_skin_type.TransformSkinType(
            extract_datetime=self.extract_datetime,
            lang_tag=self.lang_tag,
            skin_type=common.SkinType.Gathering,
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
                    cursor.execute(
                        **upsert_skin_back(
                            skin_id=skin["id"], tool=skin["details"]["type"]
                        )
                    )

                cursor.execute(query="COMMIT")
                connection.commit()
                with self.output().open("w") as w_output:
                    w_output.write("ok")

            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                raise exception_instance


def upsert_skin_back(skin_id: int, tool: str) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.skin_gathering AS target_skin_gathering
USING (
  VALUES (%(skin_id)s::integer, %(tool)s::text)
) AS source_skin_gathering (skin_id, tool)
ON
  target_skin_gathering.skin_id = source_skin_gathering.skin_id
WHEN MATCHED AND target_skin_gathering.tool != source_skin_gathering.tool THEN
  UPDATE SET
    tool = source_skin_gathering.tool
WHEN NOT MATCHED THEN
  INSERT (skin_id, tool)
    VALUES (source_skin_gathering.skin_id, source_skin_gathering.tool);
""",
        "params": {"skin_id": skin_id, "tool": tool},
    }
