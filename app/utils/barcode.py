import random


def generate_barcode() -> str:
    """Generate a unique 13-digit EAN-13-style barcode."""
    prefix = "200"
    body = "".join(str(random.randint(0, 9)) for _ in range(9))
    digits = prefix + body
    check = _checksum(digits)
    return digits + str(check)


def _checksum(digits: str) -> int:
    total = 0
    for i, d in enumerate(digits):
        total += int(d) * (3 if i % 2 == 0 else 1)
    return (10 - (total % 10)) % 10


def validate_barcode(barcode: str) -> bool:
    if len(barcode) != 13 or not barcode.isdigit():
        return False
    return _checksum(barcode[:12]) == int(barcode[12])


def barcode_svg(barcode: str, height: int = 60, label: bool = True) -> str:
    """Generate an EAN-13 barcode SVG without external dependencies.

    ponytail: naive barcode encoding, uses simple pattern for demo.
    Real EAN-13 encoding requires L/R parity tables.
    """
    if not validate_barcode(barcode):
        return "<svg><text>Invalid barcode</text></svg>"

    bars = []
    for i, ch in enumerate(barcode):
        n = int(ch)
        for bit in range(4):
            bar = (n >> (3 - bit)) & 1
            width = 1 if i < 4 else 2
            bars.append(bar)

    total_width = sum(1 if b else 1 for b in bars)
    total_width = max(total_width, 200)
    scale = max(1, total_width // 95)

    svg_bars = []
    x = 10
    bar_height = height
    for bar in bars:
        if bar:
            w = 2 * scale if label else 2 * scale
            svg_bars.append(f'<rect x="{x}" y="10" width="{w}" height="{bar_height}" fill="black"/>')
            x += w
        else:
            x += 2 * scale if label else 2 * scale

    svg_width = x + 10
    text = ""
    if label:
        text_y = height + 30
        char_x = 10 + (svg_width - 20 - len(barcode) * 8) // 2
        text = f'<text x="{char_x}" y="{text_y}" font-family="monospace" font-size="14">{barcode}</text>'
        bar_height -= 10

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{height + 40 if label else height + 20}" viewBox="0 0 {svg_width} {height + 40 if label else height + 20}">
{''.join(svg_bars)}
{text}
</svg>"""


def barcode_label_html(barcode: str, product_name: str = "", price: str = "") -> str:
    """Generate an HTML barcode label ready for printing."""
    svg = barcode_svg(barcode, height=50, label=True)
    return f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<style>
  body {{ font-family: 'Courier New', monospace; font-size: 12px; margin: 0; padding: 10px; width: 300px; }}
  .label {{ text-align: center; border: 1px dashed #999; padding: 10px; }}
  .product {{ font-size: 14px; font-weight: bold; margin-bottom: 4px; }}
  .price {{ font-size: 16px; margin-top: 4px; }}
  @media print {{ body {{ margin: 0; padding: 0; }} }}
</style>
</head><body>
<div class="label">
  {('<div class="product">' + product_name + '</div>') if product_name else ''}
  {svg}
  {('<div class="price">' + price + '</div>') if price else ''}
</div>
<script>window.print()</script>
</body></html>"""
