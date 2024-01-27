import datetime
import json
import luigi
from os import path

import common
import extract_batch


class LoadEmote(luigi.Task):
    extract_datetime = luigi.DateSecondParameter(default=datetime.datetime.now())
    output_dir = luigi.PathParameter(absolute=True, exists=True, significant=False)

    def output(self):
        target_filename = "{timestamp:s}.txt".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z")
        )
        target_path = path.join(
            self.output_dir,
            "load_emote",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        target_filename = "{timestamp:s}.ndjson".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z")
        )
        return extract_batch.ExtractBatch(
            entity_schema="../schema/gw2/v2/emotes/emote.json",
            extract_datetime=self.extract_datetime,
            extract_dir=path.join(self.output_dir, "extract_emote_id"),
            id_schema="../schema/gw2/v2/emotes/index.json",
            output_file=path.join(
                self.output_dir,
                "extract_emote",
                target_filename,
            ),
            url="https://api.guildwars2.com/v2/emotes",
        )

    def run(self):
        with (
            self.input().open("r") as ro_input_file,
            common.get_conn() as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute(query="BEGIN")
            try:
                for emote_line in ro_input_file:
                    emote = json.loads(emote_line)
                    emote_id = emote["id"]
                    cursor.execute(**upsert_emote(emote_id=emote_id))
                    emote_commands = emote["commands"]
                    cursor.execute(
                        **prune_emote_commands(
                            commands=emote_commands, emote_id=emote_id
                        )
                    )
                    cursor.execute(
                        **upsert_emote_commands(
                            commands=emote_commands, emote_id=emote_id
                        )
                    )

                cursor.execute(query="COMMIT")
                connection.commit()
                with self.output().open("w") as w_output:
                    w_output.write("ok")

            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                raise exception_instance


def upsert_emote(emote_id: str) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.emote AS target_emote
USING (
  VALUES (%(emote_id)s::text)
) AS source_emote (emote_id)
ON
  target_emote.emote_id = source_emote.emote_id
WHEN NOT MATCHED THEN
  INSERT (emote_id) VALUES (source_emote.emote_id);
""",
        "params": {"emote_id": emote_id},
    }


def prune_emote_commands(commands: list[str], emote_id: str) -> dict:
    return {
        "query": """
DELETE FROM gwapese.emote_command
WHERE emote_id = %(emote_id)s::text
  AND NOT command = ANY (%(commands)s::text[]);
""",
        "params": {"commands": commands, "emote_id": emote_id},
    }


def upsert_emote_commands(commands: list[int], emote_id: int) -> dict:
    return {
        "query": """
MERGE INTO gwapese.emote_command AS target_emote_command
USING (
  SELECT
    %(emote_id)s::text AS emote_id, command
  FROM
    unnest(%(commands)s::text[]) AS command) AS source_emote_command
ON target_emote_command.command = source_emote_command.command
  AND target_emote_command.emote_id = source_emote_command.emote_id
WHEN NOT MATCHED THEN
  INSERT (command, emote_id)
    VALUES (source_emote_command.command, source_emote_command.emote_id);
""",
        "params": {"commands": commands, "emote_id": emote_id},
    }
