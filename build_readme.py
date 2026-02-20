import re
import os

# ============================================================
# CONFIG — adjust paths and heights if you modify the SVGs
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT = os.path.join(ASSETS_DIR, "readme_full.svg")

# (name, filename, y_offset)
# Update y_offset if you change the height of any SVG
FILES = [
    ("header",   "header.svg",   0),
    ("about",    "about.svg",    230),   # header(200)   + gap(30)
    ("divider",  "divider.svg",  540),   # about(280)    + gap(30)
    ("skills",   "skills.svg",   590),   # divider(20)   + gap(30)
    ("divider",  "divider.svg",  1000),  # skills(380)   + gap(30)
    ("projects", "projects.svg", 1050),  # divider(20)   + gap(30)
    ("divider",  "divider.svg",  1420),  # projects(340) + gap(30)
    ("terminal", "terminal.svg", 1470),  # divider(20)   + gap(30)
    ("footer",   "footer.svg",   1720),  # terminal(220) + gap(30)
]

TOTAL_HEIGHT = 1780  # footer(60) + 1720

# ============================================================

def extract_style(content):
    match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
    return match.group(1).strip() if match else ""

def extract_defs_no_style(content):
    match = re.search(r'<defs>(.*?)</defs>', content, re.DOTALL)
    if not match:
        return ""
    defs = re.sub(r'<style>.*?</style>', '', match.group(1), flags=re.DOTALL)
    return defs.strip()

def extract_body(content):
    body = re.sub(r'<\?xml[^>]*\?>', '', content)
    body = re.sub(r'<svg[^>]*>', '', body)
    body = re.sub(r'</svg>', '', body)
    body = re.sub(r'<defs>.*?</defs>', '', body, flags=re.DOTALL)
    return body.strip()

# ============================================================

style_blocks = []
other_defs = []
bodies = []
seen_def_ids = set()

for name, filename, y_offset in FILES:
    path = os.path.join(ASSETS_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    style_blocks.append(f"/* === {name} === */\n{extract_style(content)}")

    raw_defs = extract_defs_no_style(content)
    if raw_defs:
        ids = re.findall(r'id="([^"]+)"', raw_defs)
        for id_val in ids:
            if id_val in seen_def_ids:
                raw_defs = re.sub(
                    rf'<[^>]+id="{re.escape(id_val)}"[^/]*/?>(?:.*?</[^>]+>)?',
                    '', raw_defs, flags=re.DOTALL
                )
            else:
                seen_def_ids.add(id_val)
        other_defs.append(raw_defs)

    bodies.append((name, y_offset, extract_body(content)))

# ============================================================

svg = f'<svg width="900" height="{TOTAL_HEIGHT}" viewBox="0 0 900 {TOTAL_HEIGHT}" xmlns="http://www.w3.org/2000/svg">\n'
svg += '<defs>\n'
svg += f'<style>\n{"".join(style_blocks)}\n</style>\n'
svg += '\n'.join(other_defs) + '\n'
svg += '</defs>\n\n'
svg += f'<rect width="900" height="{TOTAL_HEIGHT}" fill="#080808"/>\n\n'

for name, y_offset, body in bodies:
    svg += f'<!-- === {name.upper()} === -->\n'
    svg += f'<g transform="translate(0, {y_offset})">\n{body}\n</g>\n\n'

svg += '</svg>'

with open(OUTPUT, 'w', encoding='utf-8') as f:
    f.write(svg)

print(f"[ok] Built: {OUTPUT}")
print(f"  Total height : {TOTAL_HEIGHT}px")
print(f"  Total size   : {len(svg)} chars")
