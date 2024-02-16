## Rich text

GW2 supports rich text with `br` and `c` elements. `{}` represent captured values

### `c`

The `c` element opens with the expression `<c=@?(#?\w+)>`, composed from:

1. `<c=@{string}>`
1. `<c={string}>`
1. `<c=#{integer}>`

Is OPTIONALLY closed with the expression `</?c([#=@a-zA-Z0-9]+)?\s*>`, composed from:

1. `</c>`, `</c >`
1. `<c>`, `<c >`
1. `</c=@{string}>`, `</c=@{string} >`

And could converted into an CustomElements-and-XHTML-safe tag `<gw2-color value={integer | string}></gw2-color>`

### `br`

Like an HTML `br`, it is always in the form `<br>`

And could converted into an XHTML-safe tag `<br />`

### `REDACTED`

The text "<REDACTED>" must be sanitized ex `&gt;REDACTED&lt;`
