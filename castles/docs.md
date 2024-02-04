## Rich text

GW2 supports rich text with `br` and `c` elements. `{}` represent captured values

### `c`

The `c` element opens with ONE OF:

1. `<c=@{string}>`
1. `<c={string}>`
1. `<c=#{integer}>`

Is closed with ONE OF:

1. `</c>`
1. `<c>`

And is converted into an XHTML-safe tag `<gw2-color value={integer | string}></gw2-color>`

### `br`

Like an HTML `br`, it is always in the form `<br>`

And is converted into an XHTML-safe tag `<br />`
