# Brand images

SVG sources for the images in `custom_components/<domain>/brand/`, following Home
Assistant's brand image rules and the standard: one flat style, no text in the icon, the
logo's text in Inter, and no other company's logo, wordmark, product photo, or colors.

Export each SVG to PNG, trimmed, with a transparent background:

- `icon.svg` to `icon.png` (256×256) and `icon@2x.png` (512×512);
- `logo.svg` to `logo.png` (shortest side 128 to 256) and `logo@2x.png` (256 to 512);
- `dark_icon.svg` and `dark_logo.svg` the same way, as `dark_…` files.
