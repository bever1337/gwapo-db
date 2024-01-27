import datetime
import json
import luigi
from os import path

import common
import extract_batch
import load_lang


class LoadMount(luigi.Task):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    lang_tag = luigi.EnumParameter(enum=common.LangTag)
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)

    def output(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.txt".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        target_path = path.join(
            self.output_dir,
            "load_mount",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.ndjson".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        return extract_batch.ExtractBatch(
            entity_schema="../schema/gw2/v2/mounts/types/type.json",
            extract_datetime=self.extract_datetime,
            extract_dir=path.join(self.output_dir, "extract_mount_id"),
            id_schema="../schema/gw2/v2/mounts/types/index.json",
            output_file=path.join(
                self.output_dir,
                "extract_mount",
                target_filename,
            ),
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/mounts/types",
        )

    def run(self):
        with (
            self.input().open("r") as ro_input_file,
            common.get_conn() as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute(query="BEGIN")
            try:
                for mount_line in ro_input_file:
                    mount = json.loads(mount_line)
                    mount_id = mount["id"]
                    cursor.execute(**upsert_mount(mount_id=mount_id))

                    mount_name = mount["name"]
                    cursor.execute(
                        **load_lang.upsert_operating_copy(
                            app_name="gw2",
                            lang_tag=self.lang_tag.value,
                            original=mount_name,
                        )
                    )
                    cursor.execute(
                        **upsert_mount_name(
                            app_name="gw2",
                            lang_tag=self.lang_tag.value,
                            mount_id=mount_id,
                            original=mount_name,
                        )
                    )

                cursor.execute(query="COMMIT")
                connection.commit()
                with self.output().open("w") as w_output:
                    w_output.write("ok")

            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                raise exception_instance


def upsert_mount(mount_id: str) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.mount AS target_mount
USING (
  VALUES (%(mount_id)s::text)
) AS source_mount (mount_id)
ON
  target_mount.mount_id = source_mount.mount_id
WHEN NOT MATCHED THEN
  INSERT (mount_id)
    VALUES (source_mount.mount_id);
""",
        "params": {"mount_id": mount_id},
    }


def upsert_mount_name(app_name: str, lang_tag: str, original: str, mount_id: str):
    return {
        "query": """
MERGE INTO gwapese.mount_name AS target_mount_name
USING (
    VALUES (
        %(app_name)s::text,
        %(lang_tag)s::text,
        %(mount_id)s::text,
        %(original)s::text)
) AS
  source_mount_name (app_name, lang_tag, mount_id, original)
  ON target_mount_name.app_name = source_mount_name.app_name
  AND target_mount_name.lang_tag = source_mount_name.lang_tag
  AND target_mount_name.mount_id = source_mount_name.mount_id
WHEN MATCHED
  AND target_mount_name.original != source_mount_name.original THEN
  UPDATE SET
    original = source_mount_name.original
WHEN NOT MATCHED THEN
  INSERT (app_name, lang_tag, mount_id, original)
    VALUES (source_mount_name.app_name,
      source_mount_name.lang_tag,
      source_mount_name.mount_id,
      source_mount_name.original);""",
        "params": {
            "app_name": app_name,
            "lang_tag": lang_tag,
            "mount_id": mount_id,
            "original": original,
        },
    }
