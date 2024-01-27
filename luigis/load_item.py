import datetime
import json
import luigi
from os import path

import common
import extract_batch
import extract_race
import load_lang
import transform_item


class LoadItem(luigi.Task):
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
            "load_item",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        target_filename = "{timestamp:s}__lang_{lang_tag:s}.ndjson".format(
            timestamp=self.extract_datetime.strftime("%Y-%m-%dT%H%M%S%z"),
            lang_tag=self.lang_tag.value,
        )

        return {
            "item": transform_item.TransformItem(
                extract_datetime=self.extract_datetime,
                lang_tag=self.lang_tag,
                output_dir=self.output_dir,
            ),
            "profession": extract_batch.ExtractBatch(
                entity_schema="../schema/gw2/v2/professions/profession.json",
                extract_datetime=self.extract_datetime,
                extract_dir=path.join(self.output_dir, "extract_profession_id"),
                id_schema="../schema/gw2/v2/professions/index.json",
                output_file=path.join(
                    self.output_dir,
                    "extract_profession",
                    target_filename,
                ),
                url_params={
                    "lang": self.lang_tag.value,
                    "v": "2019-12-19T00:00:00.000Z",
                },
                url="https://api.guildwars2.com/v2/professions",
            ),
            "race": extract_race.ExtractRace(extract_datetime=self.extract_datetime),
        }

    def run(self):
        self.set_status_message("Starting".format(count=0))

        inputs = self.input()

        with inputs["profession"].open("r") as ro_input_file:
            professions: list[str] = [json.loads(line)["id"] for line in ro_input_file]

        with inputs["race"].open("r") as ro_input_file:
            race_names: list[str] = json.load(fp=ro_input_file)

        with (
            inputs["item"].open("r") as r_input_file,
            common.get_conn() as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute(query="BEGIN")
            # only optional keys are details and default_skin
            try:
                self.set_status_message("Count: {current:d}".format(current=0))
                for index, item_line in enumerate(r_input_file):
                    item = json.loads(item_line)
                    item_id = item["id"]
                    cursor.execute(
                        **upsert_item(
                            chat_link=item["chat_link"],
                            icon=item["icon"],
                            item_id=item_id,
                            rarity=item["rarity"],
                            required_level=item["level"],
                            vendor_value=item["vendor_value"],
                        )
                    )

                    item_description = item["description"]
                    if item_description != None:
                        cursor.execute(
                            **load_lang.upsert_operating_copy(
                                app_name="gw2",
                                lang_tag=self.lang_tag.value,
                                original=item_description,
                            )
                        )
                        cursor.execute(
                            **upsert_item_description(
                                app_name="gw2",
                                item_id=item_id,
                                lang_tag=self.lang_tag.value,
                                original=item_description,
                            )
                        )

                    item_flags = item["flags"]
                    cursor.execute(
                        **prune_item_flags(flags=item_flags, item_id=item_id)
                    )
                    for item_flag in item_flags:
                        cursor.execute(
                            **upsert_item_flag(flag=item_flag, item_id=item_id)
                        )

                    game_types = item["game_types"]
                    cursor.execute(
                        **prune_item_game_types(game_types=game_types, item_id=item_id)
                    )
                    for game_type in game_types:
                        cursor.execute(
                            **upsert_item_game_type(
                                game_type=game_type, item_id=item_id
                            )
                        )

                    profession_restrictions = [
                        restriction
                        for restriction in item["restrictions"]
                        if restriction in professions
                    ]
                    cursor.execute(
                        **prune_item_profession_restrictions(
                            item_id=item_id, profession_ids=profession_restrictions
                        )
                    )
                    for profession_id in profession_restrictions:
                        cursor.execute(
                            **upsert_item_profession_restriction(
                                profession_id=profession_id, item_id=item_id
                            )
                        )

                    race_names_restrictions = [
                        restriction
                        for restriction in item["restrictions"]
                        if restriction in race_names
                    ]
                    cursor.execute(
                        **prune_item_race_restrictions(
                            item_id=item_id, race_names=race_names_restrictions
                        )
                    )
                    for race_name in race_names_restrictions:
                        cursor.execute(
                            **upsert_item_race_restriction(
                                race_name=race_name, item_id=item_id
                            )
                        )

                    item_name = item["name"]
                    if item_name != None:
                        cursor.execute(
                            **load_lang.upsert_operating_copy(
                                app_name="gw2",
                                lang_tag=self.lang_tag.value,
                                original=item_name,
                            )
                        )
                        cursor.execute(
                            **upsert_item_name(
                                app_name="gw2",
                                item_id=item_id,
                                lang_tag=self.lang_tag.value,
                                original=item_name,
                            )
                        )

                    cursor.execute(
                        **upsert_item_type(item_id=item_id, item_type=item["type"])
                    )

                    if index % 100 == 0:
                        self.set_status_message(
                            "Count: {current:d}".format(current=index)
                        )

                cursor.execute(query="COMMIT")
                connection.commit()
                with self.output().open("w") as w_output:
                    w_output.write("ok")

            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                raise exception_instance


def upsert_item(
    chat_link: str,
    icon: str,
    item_id: int,
    rarity: str,
    required_level: int,
    vendor_value: int,
) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.item AS target_item
USING (
  VALUES (%(chat_link)s::text, %(icon)s, %(item_id)s::integer,
    %(rarity)s::text, %(required_level)s::integer, %(vendor_value)s::bigint)
) AS source_item (chat_link, icon, item_id, rarity, required_level, vendor_value)
ON
  target_item.item_id = source_item.item_id
WHEN MATCHED
  AND source_item IS DISTINCT FROM (target_item.chat_link, target_item.icon,
    target_item.item_id, target_item.rarity, target_item.required_level,
    target_item.vendor_value) THEN
  UPDATE SET
    (chat_link, icon, rarity, required_level, vendor_value) = (
      source_item.chat_link, source_item.icon, source_item.rarity,
      source_item.required_level, source_item.vendor_value)
WHEN NOT MATCHED THEN
  INSERT (chat_link, icon, item_id, rarity, required_level, vendor_value)
    VALUES (source_item.chat_link, source_item.icon, source_item.item_id,
      source_item.rarity, source_item.required_level, source_item.vendor_value);
""",
        "params": {
            "chat_link": chat_link,
            "icon": icon,
            "item_id": item_id,
            "rarity": rarity,
            "required_level": required_level,
            "vendor_value": vendor_value,
        },
    }


def upsert_item_description(
    app_name: str, item_id: int, lang_tag: str, original: str
) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.item_description AS target_item_description
USING (
VALUES (%(app_name)s::text, %(item_id)s::integer,
  %(lang_tag)s::text, %(original)s::text)
) AS source_item_description (app_name, item_id,
  lang_tag, original)
  ON target_item_description.app_name = source_item_description.app_name
  AND target_item_description.item_id = source_item_description.item_id
  AND target_item_description.lang_tag = source_item_description.lang_tag
WHEN MATCHED
  AND target_item_description.original != source_item_description.original THEN
  UPDATE SET
    original = source_item_description.original
WHEN NOT MATCHED THEN
  INSERT (app_name, item_id, lang_tag, original)
    VALUES (source_item_description.app_name,
      source_item_description.item_id,
      source_item_description.lang_tag,
      source_item_description.original);""",
        "params": {
            "app_name": app_name,
            "item_id": item_id,
            "lang_tag": lang_tag,
            "original": original,
        },
    }


def prune_item_flags(flags: list[str], item_id: int) -> dict[str]:
    return {
        "query": """
DELETE FROM gwapese.item_flag
WHERE item_id = %(item_id)s::integer
  AND NOT flag = ANY (%(flags)s::text[]);
""",
        "params": {"flags": flags, "item_id": item_id},
    }


def upsert_item_flag(flag: str, item_id: int) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.item_flag AS target_item_flag
USING (
  VALUES (%(flag)s::text, %(item_id)s::integer)
) AS source_item_flag (flag, item_id)
ON
  target_item_flag.flag = source_item_flag.flag
  AND target_item_flag.item_id = source_item_flag.item_id
WHEN NOT MATCHED THEN
  INSERT (flag, item_id)
    VALUES (source_item_flag.flag, source_item_flag.item_id);
""",
        "params": {"flag": flag, "item_id": item_id},
    }


def prune_item_game_types(game_types: list[str], item_id: int) -> dict[str]:
    return {
        "query": """
DELETE FROM gwapese.item_game_type
WHERE item_id = %(item_id)s::integer
  AND NOT game_type = ANY (%(game_types)s::text[]);
""",
        "params": {"game_types": game_types, "item_id": item_id},
    }


def upsert_item_game_type(game_type: str, item_id: int) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.item_game_type AS target_item_game_type
USING (
  VALUES (%(game_type)s::text, %(item_id)s::integer)
) AS source_item_game_type (game_type, item_id)
ON
  target_item_game_type.game_type = source_item_game_type.game_type
  AND target_item_game_type.item_id = source_item_game_type.item_id
WHEN NOT MATCHED THEN
  INSERT (game_type, item_id)
    VALUES (source_item_game_type.game_type, source_item_game_type.item_id);
""",
        "params": {"game_type": game_type, "item_id": item_id},
    }


def prune_item_profession_restrictions(
    item_id: int, profession_ids: list[str]
) -> dict[str]:
    return {
        "query": """
DELETE FROM gwapese.item_profession_restriction
WHERE item_id = %(item_id)s::integer
  AND NOT profession_id = ANY (%(profession_ids)s::text[]);
""",
        "params": {"item_id": item_id, "profession_ids": profession_ids},
    }


def upsert_item_profession_restriction(profession_id: str, item_id: int) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.item_profession_restriction AS target_item_profession_restriction
USING (
  VALUES (%(item_id)s::integer, %(profession_id)s::text)
) AS source_item_profession_restriction (item_id, profession_id)
ON
  target_item_profession_restriction.profession_id
    = source_item_profession_restriction.profession_id
  AND target_item_profession_restriction.item_id
    = source_item_profession_restriction.item_id
WHEN NOT MATCHED THEN
  INSERT (item_id, profession_id)
    VALUES (source_item_profession_restriction.item_id,
      source_item_profession_restriction.profession_id);
""",
        "params": {"profession_id": profession_id, "item_id": item_id},
    }


def prune_item_race_restrictions(item_id: int, race_names: list[str]) -> dict[str]:
    return {
        "query": """
DELETE FROM gwapese.item_race_restriction
WHERE item_id = %(item_id)s::integer
  AND NOT race_name = ANY (%(race_names)s::text[]);
""",
        "params": {"item_id": item_id, "race_names": race_names},
    }


def upsert_item_race_restriction(race_name: str, item_id: int) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.item_race_restriction AS target_item_race_restriction
USING (
  VALUES (%(item_id)s::integer, %(race_name)s::text)
) AS source_item_race_restriction (item_id, race_name)
ON
  target_item_race_restriction.item_id = source_item_race_restriction.item_id
  AND  target_item_race_restriction.race_name = source_item_race_restriction.race_name
WHEN NOT MATCHED THEN
  INSERT (item_id, race_name)
    VALUES (source_item_race_restriction.item_id,
      source_item_race_restriction.race_name);
""",
        "params": {"item_id": item_id, "race_name": race_name},
    }


def upsert_item_name(
    app_name: str, item_id: int, lang_tag: str, original: str
) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.item_name AS target_item_name
USING (
VALUES (%(app_name)s::text, %(item_id)s::integer,
  %(lang_tag)s::text, %(original)s::text)
) AS source_item_name (app_name, item_id,
  lang_tag, original)
  ON target_item_name.app_name = source_item_name.app_name
  AND target_item_name.item_id = source_item_name.item_id
  AND target_item_name.lang_tag = source_item_name.lang_tag
WHEN MATCHED
  AND target_item_name.original != source_item_name.original THEN
  UPDATE SET
    original = source_item_name.original
WHEN NOT MATCHED THEN
  INSERT (app_name, item_id, lang_tag, original)
    VALUES (source_item_name.app_name,
      source_item_name.item_id,
      source_item_name.lang_tag,
      source_item_name.original);""",
        "params": {
            "app_name": app_name,
            "item_id": item_id,
            "lang_tag": lang_tag,
            "original": original,
        },
    }


def upsert_item_type(item_id: int, item_type: str) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.item_type AS target_item_type
USING (
  VALUES (%(item_id)s::integer, %(item_type)s::text)
) AS source_item_type (item_id, item_type)
ON
  target_item_type.item_id = source_item_type.item_id
WHEN NOT MATCHED THEN
  INSERT (item_id, item_type)
    VALUES (source_item_type.item_id, source_item_type.item_type);
""",
        "params": {"item_id": item_id, "item_type": item_type},
    }


# def upsert_item_upgrade(from_item_id: int, to_item_id: int, upgrade: str) -> dict[str]:
#     return {
#         "query": """
# MERGE INTO gwapese.item_upgrade AS target_item_upgrade
# USING (
#   VALUES (%(from_item_id)s::integer, %(to_item_id)s::integer, %(upgrade)s::text)
# ) AS source_item_upgrade (from_item_id, to_item_id, upgrade)
# ON
#   target_item_upgrade.from_item_id = source_item_upgrade.from_item_id
#   AND target_item_upgrade.to_item_id = source_item_upgrade.to_item_id
#   AND target_item_upgrade.upgrade = source_item_upgrade.upgrade
# WHEN NOT MATCHED THEN
#   INSERT (from_item_id, to_item_id, upgrade)
#     VALUES (source_item_upgrade.item_id,
#       source_item_upgrade.to_item_id, source_item_upgrade.upgrade);
# """,
#         "params": {
#             "from_item_id": from_item_id,
#             "to_item_id": to_item_id,
#             "upgrade": upgrade,
#         },
#     }
