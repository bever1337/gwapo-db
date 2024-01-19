import datetime
import json
import luigi
from os import path

import common
import transform_skin_type


class LoadSkinWeapon(luigi.Task):
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
            "load_skin_weapon",
            target_filename,
        )
        return luigi.LocalTarget(path=target_path)

    def requires(self):
        return transform_skin_type.TransformSkinType(
            extract_datetime=self.extract_datetime,
            lang_tag=self.lang_tag,
            skin_type=common.SkinType.Weapon,
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
                    skin_details = skin["details"]
                    cursor.execute(
                        **upsert_skin_weapon(
                            damage_type=skin_details["damage_type"],
                            skin_id=skin["id"],
                            weapon_type=skin_details["type"],
                        )
                    )

                cursor.execute(query="COMMIT")
                connection.commit()
                with self.output().open("w") as w_output:
                    w_output.write("ok")

            except Exception as exception_instance:
                cursor.execute(query="ROLLBACK")
                raise exception_instance


def upsert_skin_weapon(damage_type: str, skin_id: int, weapon_type: str) -> dict[str]:
    return {
        "query": """
MERGE INTO gwapese.skin_weapon AS target_skin_weapon
USING (
  VALUES (%(damage_type)s::text, %(skin_id)s::smallint, %(weapon_type)s::text)
) AS source_skin_weapon (damage_type, skin_id, weapon_type)
ON
  target_skin_weapon.skin_id = source_skin_weapon.skin_id
WHEN MATCHED
  AND target_skin_weapon.damage_type != source_skin_weapon.damage_type
  OR target_skin_weapon.weapon_type != source_skin_weapon.weapon_type THEN
  UPDATE SET
    (damage_type, weapon_type) = (source_skin_weapon.damage_type, source_skin_weapon.weapon_type)
WHEN NOT MATCHED THEN
  INSERT (damage_type, skin_id, weapon_type)
    VALUES (source_skin_weapon.damage_type,
      source_skin_weapon.skin_id,
      source_skin_weapon.weapon_type);
""",
        "params": {
            "damage_type": damage_type,
            "skin_id": skin_id,
            "weapon_type": weapon_type,
        },
    }
