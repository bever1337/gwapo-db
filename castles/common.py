from dotenv import dotenv_values
import enum

import html.parser
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


class Gw2RichTextStack(html.parser.HTMLParser):
    def __init__(self, *, convert_charrefs: bool = True) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.stack: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        self.stack.pop()


# kind of gross to use _three_ languages
# xml is only an assertion step, and could be removed
def to_xhmtl_fragment(original: str):
    # convert to html
    accumulate_line = re.sub(
        pattern="<c=@?(#?\w+)>",
        repl='<gw2-color value="\\1">',
        string=original,
    )
    accumulate_line = re.sub(
        pattern="</?c([#=@a-zA-Z0-9]+)?\s?>",
        repl="</gw2-color>",
        string=accumulate_line,
    )
    accumulate_line = re.sub(
        pattern="<br>",
        repl="<br />",
        string=accumulate_line,
    )
    accumulate_line = re.sub(
        pattern="<REDACTED>", repl="&gt;REDACTED&lt;", string=accumulate_line
    )

    # close html tags, ie convert to xhtml
    parser = Gw2RichTextStack()
    parser.feed(accumulate_line)
    closing_elements = "".join(
        ["</{element}>".format(element=element) for element in parser.stack]
    )
    accumulate_line = "".join([accumulate_line, closing_elements])

    # assert as xml
    ET.fromstring(
        "<root>{accumulate_line}</root>".format(accumulate_line=accumulate_line)
    )

    return accumulate_line
