from dotenv import dotenv_values
import enum
import psycopg


def get_conn():
    config = dotenv_values("../.env")
    connection = psycopg.connect(
        conninfo="postgresql://{0}:{1}@localhost:{2}/{3}".format(
            config.get("PGUSER"),
            config.get("PGPASSWORD"),
            config.get("PGPORT"),
            config.get("PGDATABASE"),
        )
    )
    return connection


class LangTag(enum.Enum):
    En = "en"
    Es = "es"
    De = "de"
    Fr = "fr"
    Zh = "zh"


class SkinType(enum.Enum):
    Armor = "Armor"
    Back = "Back"
    Gathering = "Gathering"
    Weapon = "Weapon"