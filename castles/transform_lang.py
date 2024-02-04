import re
import xml.etree.ElementTree as ET


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
