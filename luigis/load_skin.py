import datetime
import json
import luigi
from os import path
import typing

import common
import load_lang
import transform_skin


class LoadSkin(luigi.Task):
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
            "load_skin",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        return transform_skin.TransformSkin(
            extract_datetime=self.extract_datetime, lang_tag=self.lang_tag
        )

    def run(self):
        with self.input().open("r") as ro_input_file:
            skin_json = json.load(fp=ro_input_file)

        with (
            common.get_conn() as connection,
            connection.cursor() as cursor,
        ):
            cursor.execute(query="BEGIN")
            try:
                for skin in skin_json:
                    cursor.execute(
                        **upsert_skin(
                            icon=skin["icon"], rarity=skin["rarity"], skin_id=skin["id"]
                        )
                    )

                    if skin["description"] != None:
                        cursor.execute(
                            **load_lang.upsert_operating_copy(
                                app_name="gw2",
                                lang_tag=self.lang_tag.value,
                                original=skin["description"],
                            )
                        )
                        cursor.execute(
                            **upsert_skin_description(
                                app_name="gw2",
                                lang_tag=self.lang_tag.value,
                                original=skin["description"],
                                skin_id=skin["id"],
                            )
                        )

                    cursor.execute(
                        **prune_skin_flags(flags=skin["flags"], skin_id=skin["id"])
                    )
                    for flag in skin["flags"]:
                        cursor.execute(
                            **upsert_skin_flag(flag=flag, skin_id=skin["id"])
                        )

                    if skin["name"] != None:
                        cursor.execute(
                            **load_lang.upsert_operating_copy(
                                app_name="gw2",
                                lang_tag=self.lang_tag.value,
                                original=skin["name"],
                            )
                        )
                        cursor.execute(
                            **upsert_skin_name(
                                app_name="gw2",
                                lang_tag=self.lang_tag.value,
                                original=skin["name"],
                                skin_id=skin["id"],
                            )
                        )

                    cursor.execute(
                        **prune_skin_restrictions(
                            restrictions=skin["restrictions"], skin_id=skin["id"]
                        )
                    )
                    for restriction in skin["restrictions"]:
                        cursor.execute(
                            **upsert_skin_restriction(
                                restriction=restriction, skin_id=skin["id"]
                            )
                        )

                    cursor.execute(
                        **upsert_skin_type(skin_id=skin["id"], skin_type=skin["type"])
                    )

                cursor.execute(query="COMMIT")
                connection.commit()
                with self.output().open("w") as w_output:
                    w_output.write("ok")

            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                raise exception_instance


def upsert_skin(icon: str, rarity: str, skin_id: int) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.skin AS target_skin
USING (
  VALUES (%(icon)s::text, %(rarity)s::text, %(skin_id)s::smallint)
) AS source_skin (icon, rarity, skin_id)
ON
  target_skin.skin_id = source_skin.skin_id
WHEN MATCHED
  AND target_skin.icon != source_skin.icon
  OR target_skin.rarity != source_skin.rarity THEN
  UPDATE SET
    (icon, rarity) = (source_skin.icon, source_skin.rarity)
WHEN NOT MATCHED THEN
  INSERT (icon, rarity, skin_id)
    VALUES (source_skin.icon,
      source_skin.rarity,
      source_skin.skin_id);
""",
        "params": {"icon": icon, "rarity": rarity, "skin_id": skin_id},
    }


def upsert_skin_description(
    app_name: str, lang_tag: str, original: str, skin_id: int
) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.skin_description AS target_skin_description
USING (
VALUES (%(app_name)s::text, %(lang_tag)s::text, %(original)s::text,
  %(skin_id)s::smallint)) AS source_skin_description (app_name,
  lang_tag, original, skin_id)
  ON target_skin_description.app_name = source_skin_description.app_name
  AND target_skin_description.lang_tag = source_skin_description.lang_tag
  AND target_skin_description.skin_id = source_skin_description.skin_id
WHEN MATCHED
  AND target_skin_description.original != source_skin_description.original THEN
  UPDATE SET
    original = source_skin_description.original
WHEN NOT MATCHED THEN
  INSERT (app_name, lang_tag, original, skin_id)
    VALUES (source_skin_description.app_name,
      source_skin_description.lang_tag,
      source_skin_description.original,
      source_skin_description.skin_id);""",
        "params": {
            "app_name": app_name,
            "lang_tag": lang_tag,
            "original": original,
            "skin_id": skin_id,
        },
    }


def prune_skin_flags(flags: typing.List[str], skin_id: int) -> dict[str]:
    return {
        "query": """
DELETE FROM gwapese.skin_flag
WHERE skin_id = %(skin_id)s::smallint
  AND NOT flag = ANY (%(flags)s::text[]);
""",
        "params": {"flags": flags, "skin_id": skin_id},
    }


def upsert_skin_flag(flag: str, skin_id: int) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.skin_flag AS target_skin_flag
USING (
  VALUES (%(flag)s::text, %(skin_id)s::smallint)
) AS source_skin_flag (flag, skin_id)
ON
  target_skin_flag.flag = source_skin_flag.flag
  AND target_skin_flag.skin_id = source_skin_flag.skin_id
WHEN NOT MATCHED THEN
  INSERT (flag, skin_id)
    VALUES (source_skin_flag.flag, source_skin_flag.skin_id);
""",
        "params": {"flag": flag, "skin_id": skin_id},
    }


def upsert_skin_name(
    app_name: str, lang_tag: str, original: str, skin_id: int
) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.skin_name AS target_skin_name
USING (
VALUES (%(app_name)s::text, %(lang_tag)s::text, %(original)s::text, %(skin_id)s::smallint)) AS
  source_skin_name (app_name, lang_tag, original, skin_id)
  ON target_skin_name.app_name = source_skin_name.app_name
  AND target_skin_name.lang_tag = source_skin_name.lang_tag
  AND target_skin_name.skin_id = source_skin_name.skin_id
WHEN MATCHED
  AND target_skin_name.original != source_skin_name.original THEN
  UPDATE SET
    original = source_skin_name.original
WHEN NOT MATCHED THEN
  INSERT (app_name, lang_tag, original, skin_id)
    VALUES (source_skin_name.app_name,
      source_skin_name.lang_tag,
      source_skin_name.original,
      source_skin_name.skin_id);""",
        "params": {
            "app_name": app_name,
            "lang_tag": lang_tag,
            "original": original,
            "skin_id": skin_id,
        },
    }


def prune_skin_restrictions(restrictions: typing.List[str], skin_id: int) -> dict[str]:
    return {
        "query": """
DELETE FROM gwapese.skin_restriction
WHERE skin_id = %(skin_id)s::smallint
  AND NOT restriction = ANY (%(restrictions)s::text[]);
""",
        "params": {"restrictions": restrictions, "skin_id": skin_id},
    }


def upsert_skin_restriction(restriction: str, skin_id: int) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.skin_restriction AS target_skin_restriction
USING (
  VALUES (%(restriction)s::text, %(skin_id)s::smallint)
) AS source_skin_restriction (restriction, skin_id)
ON
  target_skin_restriction.restriction = source_skin_restriction.restriction
  AND target_skin_restriction.skin_id = source_skin_restriction.skin_id
WHEN NOT MATCHED THEN
  INSERT (restriction, skin_id)
    VALUES (source_skin_restriction.restriction, source_skin_restriction.skin_id);
""",
        "params": {"restriction": restriction, "skin_id": skin_id},
    }


def upsert_skin_type(skin_id: int, skin_type: str) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.skin_type AS target_skin_type
USING (
  VALUES (%(skin_id)s::smallint, %(skin_type)s::text)
) AS source_skin_type (skin_id, skin_type)
ON
  target_skin_type.skin_id = source_skin_type.skin_id
WHEN NOT MATCHED THEN
  INSERT (skin_id, skin_type)
    VALUES (source_skin_type.skin_id, source_skin_type.skin_type);
""",
        "params": {"skin_id": skin_id, "skin_type": skin_type},
    }
