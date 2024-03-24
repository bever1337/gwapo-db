# Rich text

GW2 supports rich text with HTML-like `br` and `c` elements. A GW2 rich-text parser outputs XHTML fragments.

## Elements

### `c`

The `c` element open with one of:

1. `<c=@{string}>`
1. `<c={string}>`
1. `<c={#integer}>`

As a regular expression, `<c=@?(#?\w+)>`

The `c` element is explicitly closed with one of:

1. `</c>`, `</c >`
1. `</c=@{string}>`, `</c=@{string} >` For example, [item 91667](https://api.guildwars2.com/v2/items?ids=91667&lang=en)

Or implicitly closed with one of:

1. The beginning of the next `<c>` element
1. The end of the document fragment

As a regular expression, `</c([#=@a-zA-Z0-9]+)?\s?>`

The `c` element is renamed to a CustomElements-and-XHTML-safe tag `<gw2-color>`.

**Warning:** GW2 rich text may close tags that were never opened. The parser ignores extraneous closing tags. For example, [glider 7](https://api.guildwars2.com/v2/gliders?ids=7&lang=de).

### `br`

Like an HTML `br`, it is a void element, written `<br>`, and is converted to an XHTML-safe tag `<br />`

**Warning:** The parser treats `<br11>` as `<br>`. For example, [item 23425](https://api.guildwars2.com/v2/items?ids=23425&lang=zh)

## Text nodes

### Character escaping

- Any remaining "<" and ">" characters must be escaped. For example, the text `<REDACTED>` must be sanitized to `&lt;REDACTED&gt;`
- Sanitize "&" with `&amp;` For example, the text `PR&T皮质长靴` in [item 4864](https://api.guildwars2.com/v2/items?ids=4864&lang=zh)

### Newlines

GW2 rich text includes newlines, ie `\n`. The GW2 parser COULD

1. convert `<br />` to newline (ex., the downstream client does not make use of hypermedia)
1. convert newline to `<br />` (ex., the downstream html client would otherwise ignore concurrent whitespace)
1. treat newline as a text node and `<br />` as an element, ie do nothing (ex., the downstream html client uses default behavior)
