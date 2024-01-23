import datetime
import json
import luigi
from os import path

import common
import extract_batch
import load_lang


class LoadGuildUpgrade(luigi.Task):
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
            "load_guild_upgrade",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.json".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )
        return extract_batch.ExtractBatch(
            entity_schema="../schema/gw2/v2/guild/upgrades/guild_upgrade.json",
            extract_datetime=self.extract_datetime,
            extract_dir=path.join(self.output_dir, "extract_guild_upgrade_id"),
            id_schema="../schema/gw2/v2/guild/upgrades/index.json",
            output_file=path.join(
                self.output_dir,
                "extract_guild_upgrade",
                target_filename,
            ),
            url_params={"lang": self.lang_tag.value},
            url="https://api.guildwars2.com/v2/guild/upgrades",
        )

    def run(self):
        with self.input().open("r") as ro_input_file:
            json_input = json.load(fp=ro_input_file)

        with (
            common.get_conn() as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute(query="BEGIN")
            try:
                for guild_upgrade in json_input:
                    guild_upgrade_id = guild_upgrade["id"]
                    cursor.execute(
                        **upsert_guild_upgrade(
                            build_time=guild_upgrade["build_time"],
                            experience=guild_upgrade["experience"],
                            guild_upgrade_id=guild_upgrade_id,
                            guild_upgrade_type=guild_upgrade["type"],
                            icon=guild_upgrade["icon"],
                            required_level=guild_upgrade["required_level"],
                        )
                    )

                    guild_upgrade_description = guild_upgrade["description"]
                    if guild_upgrade_description != "":
                        cursor.execute(
                            **load_lang.upsert_operating_copy(
                                app_name="gw2",
                                lang_tag=self.lang_tag.value,
                                original=guild_upgrade_description,
                            )
                        )
                        cursor.execute(
                            **upsert_guild_upgrade_description(
                                app_name="gw2",
                                guild_upgrade_id=guild_upgrade_id,
                                lang_tag=self.lang_tag.value,
                                original=guild_upgrade_description,
                            )
                        )

                    guild_upgrade_name = guild_upgrade["name"]
                    cursor.execute(
                        **load_lang.upsert_operating_copy(
                            app_name="gw2",
                            lang_tag=self.lang_tag.value,
                            original=guild_upgrade_name,
                        )
                    )
                    cursor.execute(
                        **upsert_guild_upgrade_name(
                            app_name="gw2",
                            guild_upgrade_id=guild_upgrade_id,
                            lang_tag=self.lang_tag.value,
                            original=guild_upgrade_name,
                        )
                    )

                    cursor.execute(
                        **prune_guild_upgrade_prerequisites(
                            guild_upgrade_id=guild_upgrade_id,
                            prerequisites=guild_upgrade["prerequisites"],
                        )
                    )

                for guild_upgrade in json_input:
                    cursor.execute(
                        **upsert_guild_prerequisites(
                            guild_upgrade_id=guild_upgrade_id,
                            prerequisites=guild_upgrade["prerequisites"],
                        )
                    )

                cursor.execute(query="COMMIT")
                connection.commit()

                with self.output().open("w") as w_output:
                    w_output.write("ok")

            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                raise exception_instance


def upsert_guild_upgrade(
    build_time: int,
    experience: int,
    guild_upgrade_id: int,
    guild_upgrade_type: str,
    icon: str,
    required_level: int,
) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.guild_upgrade AS target_guild_upgrade
USING (
  VALUES (
    %(build_time)s::smallint,
    %(experience)s::smallint,
    %(guild_upgrade_id)s::smallint,
    %(guild_upgrade_type)s::text,
    %(icon)s::text,
    %(required_level)s::smallint)
) AS source_guild_upgrade (
    build_time,
    experience,
    guild_upgrade_id,
    guild_upgrade_type,
    icon,
    required_level
)
ON
  target_guild_upgrade.guild_upgrade_id = source_guild_upgrade.guild_upgrade_id
WHEN MATCHED
  AND source_guild_upgrade IS DISTINCT FROM (
    target_guild_upgrade.build_time,
    target_guild_upgrade.experience,
    target_guild_upgrade.guild_upgrade_id,
    target_guild_upgrade.guild_upgrade_type,
    target_guild_upgrade.icon,
    target_guild_upgrade.required_level
  ) THEN
  UPDATE SET
    (build_time,
      experience,
      guild_upgrade_type,
      icon,
      required_level) =
      (source_guild_upgrade.build_time,
        source_guild_upgrade.experience,
        source_guild_upgrade.guild_upgrade_type,
        source_guild_upgrade.icon,
        source_guild_upgrade.required_level)
WHEN NOT MATCHED THEN
  INSERT (build_time,
    experience,
    guild_upgrade_id,
    guild_upgrade_type,
    icon,
    required_level)
    VALUES (source_guild_upgrade.build_time,
      source_guild_upgrade.experience,
      source_guild_upgrade.guild_upgrade_id,
      source_guild_upgrade.guild_upgrade_type,
      source_guild_upgrade.icon,
      source_guild_upgrade.required_level);
""",
        "params": {
            "build_time": build_time,
            "experience": experience,
            "guild_upgrade_id": guild_upgrade_id,
            "guild_upgrade_type": guild_upgrade_type,
            "icon": icon,
            "required_level": required_level,
        },
    }


def upsert_guild_upgrade_description(
    app_name: str, guild_upgrade_id: int, lang_tag: str, original: str
):
    return {
        "query": """
MERGE INTO gwapese.guild_upgrade_description AS target_guild_upgrade_description
USING (
VALUES (%(app_name)s::text, %(guild_upgrade_id)s::smallint,
  %(lang_tag)s::text, %(original)s::text)
) AS
  source_guild_upgrade_description (app_name, guild_upgrade_id, lang_tag, original)
  ON target_guild_upgrade_description.app_name = source_guild_upgrade_description.app_name
  AND target_guild_upgrade_description.lang_tag = source_guild_upgrade_description.lang_tag
  AND target_guild_upgrade_description.guild_upgrade_id = source_guild_upgrade_description.guild_upgrade_id
WHEN MATCHED
  AND target_guild_upgrade_description.original != source_guild_upgrade_description.original THEN
  UPDATE SET
    original = source_guild_upgrade_description.original
WHEN NOT MATCHED THEN
  INSERT (app_name, guild_upgrade_id, lang_tag, original)
    VALUES (source_guild_upgrade_description.app_name,
      source_guild_upgrade_description.guild_upgrade_id,
      source_guild_upgrade_description.lang_tag,
      source_guild_upgrade_description.original);""",
        "params": {
            "app_name": app_name,
            "guild_upgrade_id": guild_upgrade_id,
            "lang_tag": lang_tag,
            "original": original,
        },
    }


def prune_guild_upgrade_prerequisites(
    guild_upgrade_id: int, prerequisites: list[int]
) -> dict:
    return {
        "query": """
DELETE FROM gwapese.guild_upgrade_prerequisite
WHERE guild_upgrade_id = %(guild_upgrade_id)s::smallint
  AND NOT prerequisite_guild_upgrade_id = ANY (%(prerequisites)s::smallint[]);
""",
        "params": {
            "prerequisites": prerequisites,
            "guild_upgrade_id": guild_upgrade_id,
        },
    }


def upsert_guild_prerequisites(guild_upgrade_id: int, prerequisites: list[int]) -> dict:
    return {
        "query": """
MERGE INTO gwapese.guild_upgrade_prerequisite AS trg
USING (
  SELECT
    %(guild_upgrade_id)s::smallint AS guild_upgrade_id, prerequisite_guild_upgrade_id
  FROM
    unnest(%(prerequisites)s::smallint[]) AS prerequisite_guild_upgrade_id) AS src
ON trg.prerequisite_guild_upgrade_id = src.prerequisite_guild_upgrade_id
  AND trg.guild_upgrade_id = src.guild_upgrade_id
WHEN NOT MATCHED THEN
  INSERT (guild_upgrade_id, prerequisite_guild_upgrade_id)
    VALUES (src.guild_upgrade_id, src.prerequisite_guild_upgrade_id);
""",
        "params": {
            "prerequisites": prerequisites,
            "guild_upgrade_id": guild_upgrade_id,
        },
    }


def upsert_guild_upgrade_name(
    app_name: str, guild_upgrade_id: int, lang_tag: str, original: str
):
    return {
        "query": """
MERGE INTO gwapese.guild_upgrade_name AS target_guild_upgrade_name
USING (
VALUES (%(app_name)s::text, %(guild_upgrade_id)s::smallint, %(lang_tag)s::text, %(original)s::text)) AS
  source_guild_upgrade_name (app_name, guild_upgrade_id, lang_tag, original)
  ON target_guild_upgrade_name.app_name = source_guild_upgrade_name.app_name
  AND target_guild_upgrade_name.lang_tag = source_guild_upgrade_name.lang_tag
  AND target_guild_upgrade_name.guild_upgrade_id = source_guild_upgrade_name.guild_upgrade_id
WHEN MATCHED
  AND target_guild_upgrade_name.original != source_guild_upgrade_name.original THEN
  UPDATE SET
    original = source_guild_upgrade_name.original
WHEN NOT MATCHED THEN
  INSERT (app_name, guild_upgrade_id, lang_tag, original)
    VALUES (source_guild_upgrade_name.app_name,
      source_guild_upgrade_name.guild_upgrade_id,
      source_guild_upgrade_name.lang_tag,
      source_guild_upgrade_name.original);""",
        "params": {
            "app_name": app_name,
            "guild_upgrade_id": guild_upgrade_id,
            "lang_tag": lang_tag,
            "original": original,
        },
    }
