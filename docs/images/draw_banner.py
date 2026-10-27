"""Draw the original README hero; standard library only, no external assets.

Run: python3 docs/images/draw_banner.py
Edit the palette, typography and parametric contour below. This is a conceptual
illustration, not CAD geometry, a toolpath or evidence of printability.
"""
from math import cos, sin, pi
from pathlib import Path

PAPER = "#f6f3e9"
INK = "#193e3b"
TEAL = "#3b756e"
ORANGE = "#c05c36"


def contour(z, inner=False):
    points = []
    for i in range(121):
        t = 2 * pi * i / 120
        r = (66 if inner else 160) * (1 + 0.10 * cos(3 * t + z * 0.018))
        x = 900 + r * cos(t) + 19 * sin(z * 0.02)
        y = 340 - z + r * sin(t) * 0.40
        points.append((x, y))
    return "M" + " L".join(f"{x:.2f},{y:.2f}" for x, y in points) + " Z"


def draw():
    svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="480" viewBox="0 0 1200 480" role="img" aria-labelledby="title desc">
<title id="title">Ideas take shape</title>
<desc id="desc">Original conceptual illustration for AI-assisted 3D design: exploratory contours surround an open, layered sculptural form. Not a CAD model, toolpath or tested physical object.</desc>
<defs>
  <radialGradient id="paper"><stop stop-color="#fffdf6"/><stop offset="1" stop-color="{PAPER}"/></radialGradient>
  <linearGradient id="layer" x1="0" x2="1"><stop stop-color="#214b46"/><stop offset="0.5" stop-color="#52877a"/><stop offset="1" stop-color="#193e3b"/></linearGradient>
  <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="0.8" fill="#193e3b" opacity="0.10"/></pattern>
</defs>
<rect width="1200" height="480" rx="20" fill="url(#paper)"/>
<path d="M640 0H1180Q1200 0 1200 20V460Q1200 480 1180 480H640Z" fill="url(#dots)"/>
<circle cx="904" cy="240" r="202" fill="none" stroke="#d6dace" stroke-width="1.5"/>
<path d="M677 399L1107 399M900 32V58M900 422V448M686 240H710M1096 240H1120" stroke="#9cae9f" stroke-width="1.5" fill="none"/>
<ellipse cx="911" cy="374" rx="174" ry="24" fill="#193e3b" opacity="0.07"/>
<g fill="none" stroke="{TEAL}" stroke-width="1.5" opacity="0.35">
<path d="M652 350C602 198 775 43 993 70C1130 89 1160 223 1095 317"/>
<path d="M675 359C634 212 785 63 994 85C1116 98 1130 223 1081 307" stroke-dasharray="6 9"/>
</g>
''']
    # Stacked closed contours suggest additive making, not measured toolpaths.
    for z in range(0, 193, 6):
        svg.append(f'<path d="{contour(z)}" fill="url(#layer)" stroke="#95b4a1" stroke-width="1.1"/>')
    svg.append(f'<path d="{contour(192)} {contour(192, True)}" fill="#dce8cd" fill-rule="evenodd" stroke="{INK}" stroke-width="1.5"/>')
    svg.append(f'<path d="{contour(192, True)}" fill="{INK}" stroke="#a7bfaa" stroke-width="2"/>')
    for z in (223, 248):
        svg.append(f'<path d="{contour(z)}" fill="none" stroke="{ORANGE}" stroke-width="2" opacity="0.8"/>')
    svg.append(f'''<g fill="{PAPER}" stroke="{ORANGE}" stroke-width="2"><circle cx="1067" cy="102" r="5"/><circle cx="758" cy="143" r="5"/></g>
<path d="M663 173C639 146 622 158 634 181C646 205 681 209 687 190C696 159 655 115 645 135" fill="none" stroke="{ORANGE}" stroke-width="2.5" stroke-linecap="round"/>
<g fill="{INK}">
<text x="58" y="94" font-family="Helvetica Neue, Helvetica, sans-serif" font-size="28" letter-spacing="2">AI-ASSISTED 3D DESIGN</text>
<g font-family="Georgia, Times New Roman, serif" font-size="88" letter-spacing="-3">
<text x="54" y="211">Ideas take</text><text x="54" y="307">shape.</text>
</g>
<path d="M59 344H126" stroke="{ORANGE}" stroke-width="5"/>
<text x="58" y="399" font-family="Helvetica Neue, Helvetica, sans-serif" font-size="30">Imagine. Make. Reimagine.</text>
</g>
</svg>''')
    return "\n".join(svg) + "\n"


if __name__ == "__main__":
    Path(__file__).with_name("readme-banner.svg").write_text(draw(), encoding="utf-8")
