from dotenv import dotenv_values
import enum
import psycopg
import re
import xml.etree.ElementTree as ET


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


def to_xhmtl_fragment(original: str):
    accumulate_line = re.sub(
        pattern="<c=@?(#?\w+)>",
        repl='<gw2-color value="\\1">',
        string=original,
    )
    accumulate_line = re.sub(
        pattern="</?c>",
        repl="</gw2-color>",
        string=accumulate_line,
    )
    accumulate_line = re.sub(
        pattern="<br>",
        repl="<br />",
        string=accumulate_line,
    )
    ET.fromstring("".join(["<root>", accumulate_line, "</root>"]))
    return accumulate_line
