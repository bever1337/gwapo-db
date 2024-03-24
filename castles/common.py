from dotenv import dotenv_values
import enum

import html.parser
import psycopg
import re
from xml.sax.saxutils import escape
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


root_name = "gw2-rich-text-root"


class Gw2RichTextStack(html.parser.HTMLParser):
    def __init__(self, *, convert_charrefs: bool = True) -> None:
        super().__init__(convert_charrefs=convert_charrefs)
        self.root = ET.Element(root_name)
        self.stack: list[ET.Element] = [self.root]

    @property
    def leaf(self) -> ET.Element | None:
        if len(self.stack) == 0:
            return None
        return self.stack[-1]

    def handle_data(self, data: str) -> None:
        escaped = escape(data=data)
        if self.leaf.tag == "br":
            self.leaf.tail = "".join([self.leaf.tail or "", escaped])
        else:
            if len(self.leaf):
                self.leaf.tail = "".join([self.leaf.tail or "", escaped])
            else:
                self.leaf.text = escaped

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "br":
            if self.leaf.tag == "br":
                self.stack.pop()
            self.stack.append(ET.SubElement(self.leaf, "br"))
        elif tag == "c":
            if self.leaf.tag == "br":
                self.stack.pop()
            if self.leaf.tag == "gw2-color":
                self.stack.pop()
            self.stack.append(ET.SubElement(self.leaf, "gw2-color", dict(attrs)))
        else:
            self.handle_data("<{tag}>".format(tag=tag))


def to_xhmtl_fragment(original: str):
    as_html = original
    for pattern, repl in (
        (r"<c=@?(#?\w+)>", '<c value="\\1">'),
        (r"</c([#=@a-zA-Z0-9]+)?\s?>", "</c>"),
        # https://api.guildwars2.com/v2/items?ids=23425&lang=zh
        (r"<br11>", "<br>"),
    ):
        as_html = re.sub(
            pattern=pattern,
            repl=repl,
            string=as_html,
        )

    parser = Gw2RichTextStack()
    parser.feed(as_html)
    as_xml = ET.tostring(element=parser.root, encoding="unicode")

    open_root = "<{tag}>".format(tag=root_name)
    close_root = "</{tag}>".format(tag=root_name)
    as_fragment = as_xml[len(open_root) : -len(close_root)]

    return as_fragment
