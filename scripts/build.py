"""Builds the animated SVG panels (light + dark) for the GitHub profile README.

All type is outlined from Inter. Flat colour, one accent. Screenshots are real
(FormaOS demo workspace, shipped LaunchNest client sites) and are embedded so
the SVGs render on GitHub. Every number shown is counted from the codebase.

Run:  python3 scripts/build.py
"""
import base64
import io
import math
from pathlib import Path

from PIL import Image

from glyphs import text, width, wrap, all_defs, reset

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / "assets"
SRC = ROOT / "source"
OUT.mkdir(exist_ok=True)

NAME_1, NAME_2 = "EJAZ", "HUSSAIN"

THEMES = {
    "dark": dict(bg="#0A0A0B", panel="#131315", panel2="#1B1B1E", line="#26262A", line2="#3A3A40",
                 text="#F2F2F3", muted="#8E8E96", faint="#55555C", accent="#2F5BFF", accent_soft="#16224F",
                 on="#FFFFFF", on_muted="#CFDAFF", deny="#FF5A47"),
    "light": dict(bg="#FFFFFF", panel="#F5F5F6", panel2="#ECECEF", line="#E3E3E7", line2="#CBCBD2",
                  text="#0A0A0B", muted="#5E5E67", faint="#A3A3AB", accent="#2F5BFF", accent_soft="#E3E9FF",
                  on="#FFFFFF", on_muted="#D9E2FF", deny="#E5402E"),
}

W = 1000
EASE = "cubic-bezier(.16,1,.3,1)"
INOUT = "cubic-bezier(.65,0,.35,1)"
REDUCED = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"

COMMON = f'''
.f{{animation:fade .9s {EASE} both}}
@keyframes fade{{from{{opacity:0;transform:translateY(12px)}}}}
.hl{{transform-box:fill-box;transform-origin:left;animation:hl 1.2s {EASE} both}}
@keyframes hl{{from{{transform:scaleX(0)}}}}
.pop{{transform-box:fill-box;transform-origin:center;animation:pop .6s {EASE} both}}
@keyframes pop{{from{{opacity:0;transform:scale(0)}}}}
.wp{{transform-box:fill-box;animation:wp 1.05s cubic-bezier(.77,0,.18,1) both}}
@keyframes wp{{0%{{transform:scaleX(0);transform-origin:left}}48%{{transform:scaleX(1);transform-origin:left}}52%{{transform:scaleX(1);transform-origin:right}}100%{{transform:scaleX(0);transform-origin:right}}}}
.on{{animation:on .01s linear both}}
@keyframes on{{from{{opacity:0}}to{{opacity:1}}}}
.up{{animation:up 1s {EASE} both}}
@keyframes up{{from{{opacity:0;transform:translateY(28px)}}}}'''


def doc(h, label, style, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{label}">
<title>{label}</title>
<style>{COMMON}
{style}
{REDUCED}</style>
{all_defs()}
{body}
</svg>
'''


def frame(T, h, fill=None):
    return f'<rect x="0.5" y="0.5" width="{W-1}" height="{h-1}" fill="{fill or T["bg"]}" stroke="{T["line"]}"/>'


def save(name, theme, svg):
    p = OUT / f"{name}-{theme}.svg"
    p.write_text(svg)
    print(f"{p.name:30s} {len(svg)/1024:7.1f} KB")


def wipe(x, y, w, h, delay, col):
    """Solid bar that sweeps in and out; content beneath appears at delay + 0.5s."""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{col}" class="wp" style="animation-delay:{delay:.2f}s"/>'


def wiped_text(s, x, y, size, col, face, delay, bar, tracking=0.0, anchor="start"):
    w = width(s, size, face, tracking)
    bx = x - (w if anchor == "end" else 0)
    return (wipe(bx - 4, y - size * 0.86, w + 8, size * 1.08, delay, bar) +
            text(s, x, y, size, col, face, anchor=anchor, tracking=tracking, cls="on", style=f"animation-delay:{delay + .5:.2f}s"))


IMG_CACHE = {}
def img(name, w, q=72, crop=None):
    key = (name, w, q, crop)
    if key not in IMG_CACHE:
        im = Image.open(SRC / name).convert("RGB")
        if crop:
            im = im.crop(crop)
        h = round(im.height * w / im.width)
        im = im.resize((w, h), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=q, optimize=True, progressive=True)
        IMG_CACHE[key] = ("data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(), w, h)
    return IMG_CACHE[key]


def cycle_css(name, i, n, slot, fade=.5, slide=24):
    """Keyframes for item i of n that is on screen during its slot of a loop of n*slot seconds."""
    D = n * slot
    p = lambda s: f"{max(0, min(100, s / D * 100)):.3f}%"
    a, b = i * slot, (i + 1) * slot
    if i == 0:
        kf = (f"0%{{opacity:1;transform:translateX(0)}}{p(b - fade)}{{opacity:1;transform:translateX(0)}}"
              f"{p(b)}{{opacity:0;transform:translateX({-slide}px)}}{p(D - fade)}{{opacity:0;transform:translateX({slide}px)}}100%{{opacity:1;transform:translateX(0)}}")
    else:
        kf = (f"0%,{p(a - fade)}{{opacity:0;transform:translateX({slide}px)}}{p(a)}{{opacity:1;transform:translateX(0)}}"
              f"{p(b - fade)}{{opacity:1;transform:translateX(0)}}{p(b)},100%{{opacity:0;transform:translateX({-slide}px)}}")
    return f".{name}{{animation:{name} {D}s {INOUT} infinite}}@keyframes {name}{{{kf}}}"


ODO = [0]
def odometer(value, x, y, size, col, face, t0, t1, D, css):
    """Rolling digit counter: digits roll to target between t0 and t1 of a D-second loop, then roll back."""
    out, cx = "", x
    cell = width("0", size, face)
    lh = size * 1.25
    nd = sum(c.isdigit() for c in value)
    k = 0
    for ch in value:
        if not ch.isdigit():
            out += text(ch, cx, y, size, col, face)
            cx += width(ch, size, face)
            continue
        ODO[0] += 1
        cid = f"od{ODO[0]}"
        target = 10 + int(ch)
        col_svg = "".join(text(str(d % 10), cx + cell / 2, y + d * lh, size, col, face, anchor="middle") for d in range(target + 1))
        a = t0 / D * 100
        b = min((t1 + (nd - 1 - k) * .12) / D * 100, 90)
        css.append(f".{cid}{{animation:{cid} {D}s cubic-bezier(.2,.7,.1,1) infinite}}"
                   f"@keyframes {cid}{{0%,{a:.2f}%{{transform:translateY(0)}}{b:.2f}%,{(D-1.4)/D*100:.2f}%{{transform:translateY({-target*lh:.1f}px)}}{(D-.3)/D*100:.2f}%,100%{{transform:translateY(0)}}}}")
        out += (f'<clipPath id="c{cid}"><rect x="{cx:.1f}" y="{y - size*0.95:.1f}" width="{cell:.1f}" height="{size*1.2:.1f}"/></clipPath>'
                f'<g clip-path="url(#c{cid})"><g class="{cid}">{col_svg}</g></g>')
        cx += cell
        k += 1
    return out


def browser(T, x, y, w, h, inner, bar=30):
    """Flat browser frame with content clipped to the viewport."""
    cid = f"bw{int(x)}{int(y)}"
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h + bar}" fill="{T["panel"]}" stroke="{T["line2"]}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{bar}" fill="{T["panel2"]}"/>'
            + "".join(f'<circle cx="{x + 18 + i*16}" cy="{y + bar/2}" r="4.5" fill="{T["line2"]}"/>' for i in range(3))
            + f'<rect x="{x + 70}" y="{y + 8}" width="{w * .42:.0f}" height="{bar - 16}" fill="{T["line"]}"/>'
            f'<clipPath id="{cid}"><rect x="{x + 1}" y="{y + bar}" width="{w - 2}" height="{h - 1}"/></clipPath>'
            f'<g clip-path="url(#{cid})">{inner}</g>')


# =====================================================================
# 01 HERO — a digital signature
# =====================================================================
AUS = [(113.4,-22.0),(114.1,-21.8),(116.7,-20.6),(118.6,-20.3),(121.0,-19.5),(122.2,-18.0),(123.5,-16.5),
       (125.0,-14.6),(126.9,-13.8),(128.1,-15.0),(129.5,-14.9),(130.1,-12.9),(130.8,-12.4),(132.6,-11.5),
       (135.9,-12.2),(136.7,-12.3),(135.9,-13.6),(135.4,-14.9),(136.8,-15.9),(139.3,-17.4),(140.8,-17.4),
       (141.6,-15.5),(141.5,-13.5),(142.0,-11.0),(142.5,-10.7),(143.5,-12.5),(143.8,-14.0),(145.3,-14.9),
       (145.8,-16.9),(146.3,-18.9),(148.8,-20.3),(150.5,-22.5),(151.3,-23.9),(153.0,-25.2),(153.1,-27.5),
       (153.6,-28.6),(153.0,-31.0),(152.0,-32.5),(151.3,-33.8),(150.8,-34.9),(150.0,-36.6),(149.9,-37.5),
       (148.0,-37.8),(146.4,-39.1),(144.9,-38.0),(143.5,-38.8),(141.6,-38.4),(140.0,-37.4),(139.6,-36.0),
       (138.9,-35.6),(138.5,-34.9),(138.0,-34.2),(137.7,-35.3),(136.9,-35.3),(137.5,-34.0),(137.8,-32.6),
       (137.0,-33.6),(135.9,-34.8),(135.1,-33.5),(134.2,-32.6),(132.3,-32.0),(129.0,-31.6),(125.0,-32.4),
       (123.6,-33.9),(121.9,-33.9),(119.8,-34.4),(117.9,-35.1),(116.0,-34.8),(115.0,-34.3),(115.6,-33.3),
       (115.7,-32.0),(115.0,-29.5),(114.6,-28.7),(114.1,-26.5),(113.2,-26.2),(113.6,-24.9)]
TAS = [(144.6,-40.7),(148.3,-40.9),(148.3,-42.2),(147.3,-43.5),(146.0,-43.6),(145.2,-42.2)]


def inside(pt, poly):
    x, y = pt
    c, j = False, len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            c = not c
        j = i
    return c


def mini_map(T, x0, y0, h):
    """Small dot-matrix Australia with Adelaide marked."""
    kx = math.cos(math.radians(27))
    lon0, lon1, lat0, lat1 = 112.9, 153.9, -10.4, -43.9
    s = h / (lat0 - lat1)
    step = 4.2
    dots, out = [], ""
    y = y0
    while y < y0 + h:
        x = x0
        while x < x0 + (lon1 - lon0) * kx * s:
            ll = ((x - x0) / (kx * s) + lon0, lat0 - (y - y0) / s)
            if inside(ll, AUS) or inside(ll, TAS):
                dots.append((x, y))
            x += step
        y += step
    ax, ay = x0 + (138.6 - lon0) * kx * s, y0 + (lat0 + 34.93) * s
    for x, y in dots:
        out += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.15" fill="{T["line2"]}"/>'
    out += f'<circle cx="{ax:.1f}" cy="{ay:.1f}" r="5" fill="none" stroke="{T["accent"]}" stroke-width="1.5" class="ring"/>'
    out += f'<circle cx="{ax:.1f}" cy="{ay:.1f}" r="3" fill="{T["accent"]}"/>'
    return out, x0 + (lon1 - lon0) * kx * s


def hero(T):
    reset()
    H, M = 700, 40
    size = 222
    tr = -0.045
    b1, b2 = 210, 392
    w1 = width(NAME_1, size, "Display-Bold", tr)
    w2 = width(NAME_2, size, "Display-Bold", tr)
    assert w2 < W - 2 * M + 10, w2

    def name_layer(col):
        return (text(NAME_1, M - 8, b1, size, col, "Display-Bold", tracking=tr) +
                text(NAME_2, M - 8, b2, size, col, "Display-Bold", tracking=tr))

    # wipe reveal for each line
    name = (wipe(M - 12, b1 - 168, w1 + 12, 176, .05, T["accent"]) +
            wipe(M - 12, b2 - 168, w2 + 12, 176, .25, T["accent"]) +
            f'<g class="on" style="animation-delay:.55s">{text(NAME_1, M - 8, b1, size, T["text"], "Display-Bold", tracking=tr)}</g>'
            f'<g class="on" style="animation-delay:.75s">{text(NAME_2, M - 8, b2, size, T["text"], "Display-Bold", tracking=tr)}</g>')

    # recurring knockout sweep: an accent bar crosses the name and inverts it
    sweep_vals = f"-260;-260;{W + 40};{W + 40}"
    anim = f'<animate attributeName="x" values="{sweep_vals}" keyTimes="0;.55;.75;1" dur="9s" begin="2.2s" repeatCount="indefinite" calcMode="spline" keySplines="0 0 1 1;.7 0 .3 1;0 0 1 1"/>'
    sweep = (f'<clipPath id="sw"><rect x="-260" y="30" width="200" height="380">{anim}</rect></clipPath>'
             f'<rect x="-260" y="30" width="200" height="380" fill="{T["accent"]}">{anim}</rect>'
             f'<g clip-path="url(#sw)">{name_layer(T["on"])}</g>')

    # positioning statement, right of EJAZ
    sx = M + w1 + 70
    stmt = ""
    for i, line in enumerate(["Founder.", "Software builder.", "Production systems."]):
        stmt += wiped_text(line, sx, 82 + i * 42, 32, T["text"] if i < 2 else T["accent"], "Display-SemiBold", .6 + i * .14, T["accent"], tracking=-.01)

    # ventures: equal size, clearly differentiated (studio = solid, product = outlined)
    cy, ch = 446, 196
    cw = (W - 2 * M - 20) / 2
    lx, fx = M, M + cw + 20
    ln = f'''<g class="up" style="animation-delay:1.1s">
<rect x="{lx}" y="{cy}" width="{cw}" height="{ch}" fill="{T["accent"]}"/>
{text("STUDIO", lx + 28, cy + 40, 13, T["on_muted"], "SemiBold", tracking=.14)}
{text("Launch Nest Studio", lx + 28, cy + 88, 36, T["on"], "Display-SemiBold", tracking=-.02)}
{"".join(text(l, lx + 28, cy + 122 + i*24, 17, T["on_muted"], "Regular") for i, l in enumerate(wrap("Custom-built websites, technical SEO and deployment for Australian businesses.", 17, cw - 56)))}
{text("launchnest.com.au", lx + 28, cy + ch - 22, 15, T["on"], "SemiBold")}
</g>'''
    fo = f'''<g class="up" style="animation-delay:1.25s">
<rect x="{fx + 1}" y="{cy + 1}" width="{cw - 2}" height="{ch - 2}" fill="{T["bg"]}" stroke="{T["text"]}" stroke-width="2"/>
{text("PRODUCT", fx + 28, cy + 40, 13, T["muted"], "SemiBold", tracking=.14)}
{text("FormaOS", fx + 28, cy + 88, 36, T["text"], "Display-SemiBold", tracking=-.02)}
{"".join(text(l, fx + 28, cy + 122 + i*24, 17, T["muted"], "Regular") for i, l in enumerate(wrap("Multi-tenant compliance platform for NDIS and care providers.", 17, cw - 56)))}
{text("formaos.com.au", fx + 28, cy + ch - 22, 15, T["text"], "SemiBold")}
</g>'''

    mm, mend = mini_map(T, M, 662, 24)
    geo = f'<g class="f" style="animation-delay:1.6s">{mm}{text("Adelaide, South Australia", mend + 14, 680, 15, T["muted"], "Medium")}</g>'

    style = f'''
.ring{{transform-box:fill-box;transform-origin:center;animation:ring 2.6s cubic-bezier(.2,.6,.3,1) infinite}}
@keyframes ring{{0%{{transform:scale(.5);opacity:1}}100%{{transform:scale(2.6);opacity:0}}}}'''
    body = f'''{frame(T, H)}
{name}
{sweep}
{stmt}
{ln}
{fo}
{geo}'''
    return doc(H, "Ejaz Hussain. Founder. Software builder. Production systems. Launch Nest Studio and FormaOS. Adelaide, South Australia.", style, body)


# =====================================================================
# 02 SELECTED WORK — FormaOS
# =====================================================================
def case_header(T, kicker, title, sub, M=40):
    return (text(kicker, M, 58, 13, T["muted"], "SemiBold", tracking=.14, cls="f") +
            wiped_text(title, M, 128, 64, T["text"], "Display-Bold", .1, T["accent"], tracking=-.03) +
            text(sub, M, 168, 20, T["muted"], "Regular", cls="f", style="animation-delay:.6s"))


def columns(T, items, x0, y0, total_w, cols, gap=24, delay=1.0):
    cw = (total_w - gap * (cols - 1)) / cols
    out = ""
    for i, (t, body) in enumerate(items):
        x = x0 + (i % cols) * (cw + gap)
        y = y0 + (i // cols) * 150
        d = delay + i * .1
        out += f'<g class="f" style="animation-delay:{d:.2f}s">'
        out += f'<rect x="{x}" y="{y}" width="28" height="3" fill="{T["accent"]}"/>'
        out += text(t, x, y + 32, 18, T["text"], "SemiBold")
        for j, l in enumerate(wrap(body, 15, cw - 4)):
            out += text(l, x, y + 58 + j * 21, 15, T["muted"], "Regular")
        out += "</g>"
    return out


def work_formaos(T):
    reset()
    H, M, D = 960, 40, 16
    css = []
    body = frame(T, H)
    body += case_header(T, "SELECTED WORK  01", "FormaOS", "Multi-tenant compliance platform for Australian NDIS and care providers.")

    # desktop screens cycling in a browser frame, phone screens cycling alongside
    bx, by, bw = M, 206, 660
    desks = ["formaos-home.webp", "formaos-roster.webp", "formaos-participants.webp", "formaos-incidents.webp"]
    slot = D / len(desks)
    inner = ""
    for i, f in enumerate(desks):
        uri, iw, ih = img(f, 1100, 70)
        h = bw * ih / iw
        css.append(cycle_css(f"dk{i}", i, len(desks), slot))
        inner += f'<g class="dk{i}"><image href="{uri}" x="{bx}" y="{by + 30}" width="{bw}" height="{h:.1f}" preserveAspectRatio="xMidYMin slice"/></g>'
    bh = bw * 1640 / 2880
    body += f'<g class="up" style="animation-delay:.5s">{browser(T, bx, by, bw, bh, inner)}</g>'

    px, py, pw, ph = 720, 236, 196, 392
    phones = ["formaos-home-phone.webp", "formaos-roster-phone.webp", "formaos-home-phone.webp", "formaos-incidents-phone.webp"]
    pin = ""
    for i, f in enumerate(phones):
        uri, iw, ih = img(f, 420, 72)
        css.append(cycle_css(f"ph{i}", i, len(phones), slot, slide=0))
        pin += f'<g class="ph{i}"><image href="{uri}" x="{px}" y="{py}" width="{pw}" height="{pw * ih / iw:.1f}"/></g>'
    body += (f'<g class="up" style="animation-delay:.7s"><rect x="{px - 10}" y="{py - 10}" width="{pw + 20}" height="{ph + 20}" fill="{T["text"]}"/>'
             f'<clipPath id="phc"><rect x="{px}" y="{py}" width="{pw}" height="{ph}"/></clipPath><g clip-path="url(#phc)">{pin}</g></g>')
    labels = ["Home", "Roster", "Participants", "Incidents"]
    for i, l in enumerate(labels):
        css.append(cycle_css(f"lb{i}", i, len(labels), slot, slide=10))
        body += f'<g class="lb{i}">{text(l, bx, by + bh + 64, 15, T["muted"], "Medium")}</g>'
    # slot progress ticks
    for i in range(len(labels)):
        tx = bx + bw - (len(labels) - i) * 36
        body += f'<rect x="{tx}" y="{by + bh + 54}" width="28" height="3" fill="{T["line2"]}"/>'
        k = f"pt{i}"
        a, b = i * slot / D * 100, (i + 1) * slot / D * 100
        css.append(f".{k}{{transform-box:fill-box;transform-origin:left;animation:{k} {D}s linear infinite}}"
                   f"@keyframes {k}{{0%,{a:.2f}%{{transform:scaleX(0)}}{b:.2f}%{{transform:scaleX(1)}}{min(b+.01,100):.2f}%,100%{{transform:scaleX(0)}}}}")
        body += f'<rect x="{tx}" y="{by + bh + 54}" width="28" height="3" fill="{T["accent"]}" class="{k}"/>'

    items = [
        ("Tenant isolation", "Row-level security on every tenant table, enforced by a lint rule and live contract tests."),
        ("Permissions", "MFA gate, SSO and a server-side permission engine checked before data is touched."),
        ("Billing", "Stripe subscriptions with a nightly reconciliation job and grace-period enforcement."),
        ("Compliance", "12 framework packs, including NDIS and ISO 27001, plus regulator deadline clocks."),
        ("Automated QA", "Playwright, Jest, accessibility and visual regression run on every pull request."),
    ]
    body += columns(T, items, M, 690, W - 2 * M, 5, gap=22, delay=1.0)

    # verified numbers, counted from the repository
    sy = 870
    body += f'<rect x="{M}" y="{sy}" width="{W - 2*M}" height="1" fill="{T["line"]}" class="hl" style="animation-delay:1.3s"/>'
    stats = [("300", "API routes"), ("358", "database migrations"), ("81", "Playwright specs"), ("632", "test files"), ("12", "CI workflows")]
    sw = (W - 2 * M) / len(stats)
    for i, (v, l) in enumerate(stats):
        x = M + i * sw
        body += odometer(v, x, sy + 52, 30, T["text"], "Display-SemiBold", 1.4 + i * .15, 3.0 + i * .15, D, css)
        body += text(l, x, sy + 76, 14, T["muted"], "Medium", cls="f", style=f"animation-delay:{1.5 + i*.1:.2f}s")

    return doc(H, "FormaOS case study: real product screens, technical challenges and counts from the codebase", "".join(css), body)


# =====================================================================
# 02 SELECTED WORK — LaunchNest
# =====================================================================
def work_launchnest(T):
    reset()
    H, M, D = 950, 40, 15
    css = []
    body = frame(T, H)
    body += case_header(T, "SELECTED WORK  02", "Launch Nest Studio", "Custom-built production websites for Australian businesses.")

    sites = [("ln-build-pro-2.jpg", "Build Pro", "buildprocorporation.com.au"),
             ("ln-dandy-rugs-2.jpg", "Dandy Rugs", "dandyrugs.com.au"),
             ("ln-batoor.jpg", "Barat Ali Batoor", "batoor.com"),
             ("ln-qclub.jpg", "Q Club", "Adelaide pool and billiards"),
             ("ln-sa-best-towing.jpg", "SA Best Towing", "24/7 towing, Adelaide")]
    slot = D / len(sites)
    bx, by, bw = M, 206, 640
    bh = bw * 1000 / 1600
    inner, caps = "", ""
    for i, (f, name, sub) in enumerate(sites):
        uri, iw, ih = img(f, 1000, 70)
        css.append(cycle_css(f"st{i}", i, len(sites), slot))
        inner += f'<g class="st{i}"><image href="{uri}" x="{bx}" y="{by + 30}" width="{bw}" height="{bw * ih / iw:.1f}"/></g>'
        css.append(cycle_css(f"sc{i}", i, len(sites), slot, slide=12))
        caps += f'<g class="sc{i}">{text(name, bx, by + bh + 70, 22, T["text"], "SemiBold")}{text(sub, bx, by + bh + 96, 15, T["muted"], "Regular")}</g>'
    body += f'<g class="up" style="animation-delay:.5s">{browser(T, bx, by, bw, bh, inner)}</g>' + caps
    for i in range(len(sites)):
        tx = bx + bw - (len(sites) - i) * 36
        body += f'<rect x="{tx}" y="{by + bh + 54}" width="28" height="3" fill="{T["line2"]}"/>'
        k = f"pt{i}"
        a, b = i * slot / D * 100, (i + 1) * slot / D * 100
        css.append(f".{k}{{transform-box:fill-box;transform-origin:left;animation:{k} {D}s linear infinite}}"
                   f"@keyframes {k}{{0%,{a:.2f}%{{transform:scaleX(0)}}{b:.2f}%{{transform:scaleX(1)}}{min(b+.01,100):.2f}%,100%{{transform:scaleX(0)}}}}")
        body += f'<rect x="{tx}" y="{by + bh + 54}" width="28" height="3" fill="{T["accent"]}" class="{k}"/>'

    # full-page capture scrolling in a tall frame
    tx, ty, tw, th = 712, 206, 248, bh + 30
    uri, iw, ih = img("ln-build-pro-page-2.jpg", 500, 70)
    full_h = tw * ih / iw
    travel = full_h - th
    css.append(f".scr{{animation:scr 14s {INOUT} infinite alternate}}@keyframes scr{{0%,8%{{transform:translateY(0)}}92%,100%{{transform:translateY({-travel:.1f}px)}}}}")
    body += (f'<g class="up" style="animation-delay:.7s"><rect x="{tx}" y="{ty}" width="{tw}" height="{th}" fill="{T["panel"]}" stroke="{T["line2"]}"/>'
             f'<clipPath id="tall"><rect x="{tx + 1}" y="{ty + 1}" width="{tw - 2}" height="{th - 2}"/></clipPath>'
             f'<g clip-path="url(#tall)"><g class="scr"><image href="{uri}" x="{tx}" y="{ty}" width="{tw}" height="{full_h:.1f}"/></g></g></g>')
    body += text("Full page, Build Pro", tx, by + bh + 70, 15, T["muted"], "Medium", cls="f", style="animation-delay:1s")

    items = [
        ("No page builders", "Hand-built Next.js and TypeScript sites with GSAP motion, or custom WordPress themes where a client needs a CMS."),
        ("Technical SEO", "Server-rendered pages, generated sitemaps and robots rules, structured data and Core Web Vitals tracking."),
        ("Deployment engineering", "Vercel deploys with analytics, speed insights and bot protection, backed by Playwright and Vitest suites."),
    ]
    body += columns(T, items, M, 760, W - 2 * M, 3, gap=36, delay=1.0)
    return doc(H, "Launch Nest Studio case study: shipped client websites for Build Pro, Dandy Rugs, Barat Ali Batoor, Q Club and SA Best Towing", "".join(css), body)


# =====================================================================
# 03 ARCHITECTURE — tenant isolation as the story
# =====================================================================
def architecture(T):
    reset()
    H, D = 700, 12
    css = []
    pct = lambda s: f"{s / D * 100:.2f}%"
    L, R = 40, 600            # diagram band
    CX = 640                  # callouts column
    bands = [("CLIENTS", 40), ("APPLICATION", 190), ("DATA", 340), ("SERVICES", 540)]
    bh = [120, 130, 180, 110]
    body = frame(T, H)
    for i, (name, y) in enumerate(bands):
        body += f'<g class="f" style="animation-delay:{i*.1:.2f}s"><rect x="{L}" y="{y}" width="{R - L}" height="{bh[i]}" fill="{T["panel"]}" stroke="{T["line"]}"/>'
        body += text(name, L + 20, y + 30, 12, T["muted"], "SemiBold", tracking=.14) + "</g>"

    def node(x, y, w, h, label, d, stroke=None, fill=None):
        return (f'<g class="f" style="animation-delay:{d:.2f}s"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill or T["bg"]}" stroke="{stroke or T["line2"]}"/>'
                + text(label, x + w / 2, y + h / 2 + 6, 15, T["text"], "Medium", anchor="middle") + "</g>")

    nw = 118
    cl = ["Web app", "iOS", "Android", "Auditor portal"]
    for i, c in enumerate(cl):
        body += node(L + 20 + i * (nw + 12), 88, nw, 46, c, .2 + i * .05)
    ap = [("Auth + MFA", 150), ("Permission engine", 180), ("API routes", 150)]
    x = L + 20
    app_x = {}
    for a, w in ap:
        body += node(x, 238, w, 46, a, .4)
        app_x[a] = (x, w)
        x += w + 12
    body += text("Next.js on Vercel, Sydney region", L + 20, 306, 14, T["muted"], "Regular", cls="f", style="animation-delay:.5s")

    # tenants inside the data band, separated by RLS walls
    tw = (R - L - 40 - 2 * 14) / 3
    tenants = ["Tenant A", "Tenant B", "Tenant C"]
    tx = [L + 20 + i * (tw + 14) for i in range(3)]
    ty, th = 386, 106
    for i, t in enumerate(tenants):
        body += f'<g class="f" style="animation-delay:{.6 + i*.06:.2f}s"><rect x="{tx[i]:.1f}" y="{ty}" width="{tw:.1f}" height="{th}" fill="{T["bg"]}" stroke="{T["line2"]}"/>'
        body += text(t, tx[i] + 16, ty + 30, 15, T["text"], "SemiBold")
        for r in range(3):
            body += f'<rect x="{tx[i] + 16:.1f}" y="{ty + 46 + r*16}" width="{tw - 32:.1f}" height="9" fill="{T["line"]}"/>'
        body += "</g>"
    for i in range(1, 3):
        wx = tx[i] - 7
        body += f'<rect x="{wx - 2:.1f}" y="{ty - 8}" width="4" height="{th + 16}" fill="{T["text"]}" class="f" style="animation-delay:.8s"/>'
    body += text("Supabase Postgres, RLS on every tenant table", L + 20, 514, 14, T["muted"], "Regular", cls="f", style="animation-delay:.7s")

    sv = ["Sentry", "Resend", "Trigger.dev", "Stripe"]
    for i, s in enumerate(sv):
        body += node(L + 20 + i * (nw + 12), 584, nw, 46, s, .9 + i * .05)

    # ---- the request story (timed, looping)
    def timed(kind, t_on, t_off=None):
        k = f"t{len(css)}"
        a = t_on / D * 100
        off = f"{t_off / D * 100:.2f}%{{opacity:1}}{(t_off + .3) / D * 100:.2f}%,100%{{opacity:0}}" if t_off else "100%{opacity:1}"
        css.append(f".{k}{{animation:{k} {D}s {EASE} infinite}}@keyframes {k}{{0%,{a:.2f}%{{opacity:0}}{(t_on + .3) / D * 100:.2f}%{{opacity:1}}{off}}}")
        return k

    def move(path, t0, t1, col):
        a, b = t0 / D, t1 / D
        return (f'<path d="{path}" pathLength="1" fill="none" stroke="{col}" stroke-width="2.5" class="{draw(t0, t1)}"/>'
                f'<rect x="-6" y="-6" width="12" height="12" fill="{col}" opacity="0">'
                f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;{a:.4f};{b:.4f}" calcMode="discrete" dur="{D}s" repeatCount="indefinite"/>'
                f'<animateMotion path="{path}" dur="{D}s" repeatCount="indefinite" keyTimes="0;{a:.4f};{b:.4f};1" keyPoints="0;0;1;1" calcMode="linear"/></rect>')

    def draw(t0, t1):
        k = f"t{len(css)}"
        css.append(f".{k}{{stroke-dasharray:1;animation:{k} {D}s linear infinite}}@keyframes {k}{{0%,{pct(t0)}{{stroke-dashoffset:1;opacity:1}}{pct(t1)},{pct(9.6)}{{stroke-dashoffset:0;opacity:1}}{pct(10)},100%{{stroke-dashoffset:0;opacity:0}}}}")
        return k

    A = T["accent"]
    web_cx = L + 20 + nw / 2
    auth_x, auth_w = app_x["Auth + MFA"]
    perm_x, perm_w = app_x["Permission engine"]
    story = ""
    story += f'<rect x="{L + 20}" y="88" width="{nw}" height="46" fill="none" stroke="{A}" stroke-width="2.5" class="{timed("o", .6, 9.6)}"/>'
    story += move(f"M{web_cx} 134 V238", .8, 1.6, A)
    story += f'<rect x="{auth_x}" y="238" width="{auth_w}" height="46" fill="none" stroke="{A}" stroke-width="2.5" class="{timed("o", 1.6, 9.6)}"/>'
    story += move(f"M{auth_x + auth_w} 261 H{perm_x}", 1.9, 2.4, A)
    story += f'<rect x="{perm_x}" y="238" width="{perm_w}" height="46" fill="none" stroke="{A}" stroke-width="2.5" class="{timed("o", 2.4, 9.6)}"/>'
    pa = perm_x + perm_w / 2
    ta = tx[0] + tw / 2
    story += move(f"M{pa} 284 V330 H{ta:.1f} V{ty}", 2.8, 3.8, A)
    story += f'<rect x="{tx[0]:.1f}" y="{ty}" width="{tw:.1f}" height="{th}" fill="{A}" fill-opacity=".16" stroke="{A}" stroke-width="2.5" class="{timed("o", 3.8, 9.6)}"/>'
    # cross-tenant attempt, denied at the wall
    tb = tx[1] + tw / 2
    wall = tx[1] - 7
    story += move(f"M{ta:.1f} {ty + th/2} H{wall - 8:.1f}", 5.0, 5.7, T["deny"])
    story += (f'<g class="{timed("o", 5.7, 9.6)}"><circle cx="{wall:.1f}" cy="{ty + th/2}" r="15" fill="{T["deny"]}"/>'
              f'<path d="M{wall - 6:.1f} {ty + th/2 - 6} L{wall + 6:.1f} {ty + th/2 + 6} M{wall + 6:.1f} {ty + th/2 - 6} L{wall - 6:.1f} {ty + th/2 + 6}" stroke="{T["on"]}" stroke-width="3" stroke-linecap="round"/></g>')
    story += f'<g class="{timed("o", 5.9, 9.6)}">{text("0 rows", tb, ty + th/2 + 6, 16, T["deny"], "SemiBold", anchor="middle")}</g>'
    # billing
    api_x, api_w = app_x["API routes"]
    sx0 = L + 20 + 3 * (nw + 12)
    sx = sx0 + nw / 2
    story += move(f"M{api_x + api_w/2} 284 V326 H{R - 10} V530 H{sx} V584", 7.0, 8.2, A)
    story += f'<rect x="{sx0}" y="584" width="{nw}" height="46" fill="none" stroke="{A}" stroke-width="2.5" class="{timed("o", 8.2, 9.6)}"/>'
    body += story

    # ---- callouts, each lights up when its step happens
    calls = [
        ("1", "Authorization", "MFA gate and a server-side permission engine check roles before any query runs.", 1.6, 261),
        ("2", "Row-level security", "Every tenant table carries RLS policies. A query outside the caller's organisation returns nothing.", 5.7, 439),
        ("3", "Billing", "Stripe subscriptions, a nightly reconciliation job and automatic grace-period enforcement.", 8.2, 607),
        ("4", "Automated testing", "A lint rule blocks unscoped tenant queries, and RLS contract tests run against a live database in CI.", 9.0, None),
    ]
    cy = 40
    for n, title, desc, t_on, anchor_y in calls:
        lines = wrap(desc, 15, W - CX - 80)
        hgt = 52 + len(lines) * 21
        k = timed("o", t_on, 9.6)
        body += f'<g class="f" style="animation-delay:{1 + int(n)*.1:.2f}s">'
        body += f'<rect x="{CX}" y="{cy}" width="{W - CX - 40}" height="{hgt}" fill="{T["bg"]}" stroke="{T["line"]}"/>'
        body += f'<rect x="{CX}" y="{cy}" width="{W - CX - 40}" height="{hgt}" fill="{A}" fill-opacity=".1" stroke="{A}" stroke-width="2" class="{k}"/>'
        body += f'<rect x="{CX + 18}" y="{cy + 18}" width="24" height="24" fill="{T["text"]}"/>'
        body += f'<rect x="{CX + 18}" y="{cy + 18}" width="24" height="24" fill="{A}" class="{k}"/>'
        body += text(n, CX + 30, cy + 36, 14, T["bg"], "Bold", anchor="middle")
        body += f'<g class="{k}">{text(n, CX + 30, cy + 36, 14, T["on"], "Bold", anchor="middle")}</g>'
        body += text(title, CX + 54, cy + 36, 18, T["text"], "SemiBold")
        for j, l in enumerate(lines):
            body += text(l, CX + 18, cy + 66 + j * 21, 15, T["muted"], "Regular")
        body += "</g>"
        if anchor_y:
            mid = cy + 30
            body += f'<path d="M{R} {anchor_y} H{R + 16} V{mid} H{CX}" fill="none" stroke="{A}" stroke-width="1.5" stroke-dasharray="3 4" class="{k}"/>'
        cy += hgt + 16
    # CI badge on the data band for callout 4
    k4 = timed("o", 9.0, 9.6)
    body += f'<g class="{k4}"><rect x="{R - 96}" y="352" width="58" height="24" fill="{A}"/>{text("CI", R - 67, 369, 13, T["on"], "Bold", anchor="middle")}</g>'
    return doc(H, "FormaOS architecture: clients, application, data and services. A request is authorised, reads its own tenant, is denied by row-level security when it reaches another tenant, and billing runs through Stripe.", "".join(css), body)


# =====================================================================
# 04 ENGINEERING PROCESS — what the pipeline actually runs
# =====================================================================
def process(T):
    reset()
    H, D, M = 580, 14, 40
    css = []
    pct = lambda s: f"{s / D * 100:.2f}%"
    body = frame(T, H)
    stages = [("Pull request", "Feature branch"), ("Quality gates", "Every PR and push"), ("Deployment gates", "Blocks on failure"),
              ("Production", "Vercel, Sydney"), ("Post-deploy", "Validation, rollback"), ("Monitoring", "Sentry, PostHog")]
    ty = 96
    x0, x1 = 90, W - 90
    step = (x1 - x0) / (len(stages) - 1)
    times = [.6, 1.4, 7.0, 8.0, 9.0, 10.0]

    def timed(t_on, k_pref="t"):
        k = f"{k_pref}{len(css)}"
        css.append(f".{k}{{animation:{k} {D}s {EASE} infinite}}@keyframes {k}{{0%,{pct(t_on)}{{opacity:0}}{pct(t_on + .3)},{pct(D - .8)}{{opacity:1}}{pct(D - .3)},100%{{opacity:0}}}}")
        return k

    body += f'<rect x="{x0}" y="{ty - 1.5}" width="{x1 - x0}" height="3" fill="{T["line2"]}"/>'
    # progress line follows the stage times
    kf = ["0%{transform:scaleX(0)}"] + [f"{pct(t)}{{transform:scaleX({i/(len(stages)-1):.4f})}}" for i, t in enumerate(times)] + [f"{pct(D - .8)}{{transform:scaleX(1);opacity:1}}{pct(D - .3)},100%{{transform:scaleX(1);opacity:0}}"]
    css.append(f".prog{{transform-box:fill-box;transform-origin:left;animation:prog {D}s {INOUT} infinite}}@keyframes prog{{{''.join(kf)}}}")
    body += f'<rect x="{x0}" y="{ty - 1.5}" width="{x1 - x0}" height="3" fill="{T["accent"]}" class="prog"/>'
    for i, (s, sub) in enumerate(stages):
        x = x0 + i * step
        body += f'<circle cx="{x:.1f}" cy="{ty}" r="10" fill="{T["bg"]}" stroke="{T["line2"]}" stroke-width="3"/>'
        body += f'<circle cx="{x:.1f}" cy="{ty}" r="10" fill="{T["accent"]}" class="{timed(times[i])}"/>'
        body += text(s, x, ty - 30, 16, T["text"], "SemiBold", anchor="middle", cls="f", style=f"animation-delay:{i*.08:.2f}s")
        body += text(sub, x, ty + 40, 14, T["muted"], "Regular", anchor="middle", cls="f", style=f"animation-delay:{.1 + i*.08:.2f}s")

    # the checks that actually run (from .github/workflows)
    checks = [("Type check", "tsc --noEmit"), ("ESLint", "Warning ceiling ratchet"), ("Tenant-isolation lint", "Unscoped queries fail the build"),
              ("Jest", "Unit and integration, with coverage"), ("RLS contract tests", "Against a live Supabase database"),
              ("Playwright", "End-to-end suite"), ("Accessibility", "axe-core audits"), ("Visual regression", "Screenshot diffs"),
              ("Lighthouse CI", "Performance budgets"), ("Security scans", "npm audit, CodeQL, secret detection")]
    gx, gy = M, 190
    body += text("QUALITY GATES, RUN ON EVERY PULL REQUEST", gx, gy, 12, T["muted"], "SemiBold", tracking=.14, cls="f", style="animation-delay:.4s")
    cw = (W - 2 * M - 30) / 2
    rh = 66
    for i, (t, sub) in enumerate(checks):
        cx = gx + (i // 5) * (cw + 30)
        cy = gy + 22 + (i % 5) * rh
        t_on = 1.8 + i * .5
        body += f'<g class="f" style="animation-delay:{.5 + i*.05:.2f}s"><rect x="{cx}" y="{cy}" width="{cw:.1f}" height="{rh - 10}" fill="{T["panel"]}" stroke="{T["line"]}"/>'
        body += text(t, cx + 58, cy + 25, 16, T["text"], "SemiBold")
        body += text(sub, cx + 58, cy + 45, 14, T["muted"], "Regular")
        body += f'<rect x="{cx + 18}" y="{cy + 15}" width="26" height="26" fill="none" stroke="{T["line2"]}" stroke-width="2"/></g>'
        k = timed(t_on)
        body += (f'<g class="{k}"><rect x="{cx + 18}" y="{cy + 15}" width="26" height="26" fill="{T["accent"]}"/>'
                 f'<path d="M{cx + 24} {cy + 28} L{cx + 29} {cy + 33} L{cx + 38} {cy + 22}" fill="none" stroke="{T["on"]}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></g>')
        # running indicator before it passes
        kr = f"r{len(css)}"
        css.append(f".{kr}{{transform-box:fill-box;transform-origin:left;animation:{kr} {D}s linear infinite}}@keyframes {kr}{{0%,{pct(t_on - .5)}{{transform:scaleX(0);opacity:1}}{pct(t_on)}{{transform:scaleX(1);opacity:1}}{pct(t_on + .2)},100%{{transform:scaleX(1);opacity:0}}}}")
        body += f'<rect x="{cx}" y="{cy + rh - 13}" width="{cw:.1f}" height="3" fill="{T["accent"]}" class="{kr}"/>'
    return doc(H, "Engineering process: pull request, quality gates (type check, ESLint, tenant-isolation lint, Jest, RLS contract tests, Playwright, accessibility, visual regression, Lighthouse CI, security scans), deployment gates, production on Vercel, post-deploy validation and monitoring with Sentry, PostHog and OpenTelemetry.", "".join(css), body)


# =====================================================================
# 05 STACK — six that define the work
# =====================================================================
def stack(T):
    reset()
    H, M = 430, 40
    tiles = [("Next.js", "App Router, 300 API routes"), ("TypeScript", "Type-checked on every PR"),
             ("PostgreSQL", "358 migrations, RLS throughout"), ("Supabase", "Auth, Postgres, realtime"),
             ("Playwright", "81 end-to-end specs in CI"), ("Vercel", "Production in Sydney, 25 cron jobs")]
    gap = 16
    tw = (W - 2 * M - 2 * gap) / 3
    th = 132
    body = frame(T, H)
    for i, (n, d) in enumerate(tiles):
        x = M + (i % 3) * (tw + gap)
        y = M + (i // 3) * (th + gap)
        dl = .1 + i * .1
        body += f'<g class="up" style="animation-delay:{dl:.2f}s"><rect x="{x:.1f}" y="{y}" width="{tw:.1f}" height="{th}" fill="{T["panel"]}" stroke="{T["line"]}"/></g>'
        body += wiped_text(n, x + 24, y + 64, 36, T["text"], "Display-SemiBold", dl + .3, T["accent"], tracking=-.02)
        body += text(d, x + 24, y + 100, 15, T["muted"], "Regular", cls="f", style=f"animation-delay:{dl + .7:.2f}s")
    also = "Also: Stripe, Sentry, PostHog, OpenTelemetry, Jest, Tailwind CSS, Resend, Trigger.dev, Upstash Redis, GSAP, WordPress"
    lines = wrap(also, 16, W - 2 * M)
    for j, l in enumerate(lines):
        body += text(l, M, M + 2 * th + gap + 50 + j * 24, 16, T["muted"], "Regular", cls="f", style=f"animation-delay:{1.2 + j*.1:.2f}s")
    return doc(H, "Stack: Next.js, TypeScript, PostgreSQL, Supabase, Playwright, Vercel. Also Stripe, Sentry, PostHog, OpenTelemetry, Jest, Tailwind CSS, Resend, Trigger.dev, Upstash Redis, GSAP, WordPress.", "", body)


# =====================================================================
# CONTACT
# =====================================================================
def contact(T):
    reset()
    H, M = 280, 52
    url = "launchnest.com.au"
    uw = width(url, 78, "Display-SemiBold", tracking=-.025)
    ax = M + uw + 30
    body = frame(T, H, T["accent"])
    body += (f'<clipPath id="cc"><rect x="1" y="1" width="{W-2}" height="{H-2}"/></clipPath><g clip-path="url(#cc)">' +
             "".join(f'<circle cx="{ax + 26:.1f}" cy="142" r="700" fill="none" stroke="{T["on"]}" stroke-opacity=".14" stroke-width="1.5" vector-effect="non-scaling-stroke" class="wave" style="animation-delay:{i*2.4:.1f}s"/>' for i in range(5)) +
             "</g>")
    body += text("Have a project in mind?", M, 82, 22, T["on_muted"], "Regular", cls="f")
    body += text(url, M - 3, 172, 78, T["on"], "Display-SemiBold", tracking=-.025,
                 per_glyph=lambda i, ch: ("g", f"animation-delay:{.15 + i*.03:.2f}s"))
    body += f'<rect x="{M}" y="196" width="{uw:.1f}" height="4" fill="{T["on"]}" class="ul"/>'
    body += f'<g class="arw"><path d="M{ax + 6:.1f} 162 L{ax + 46:.1f} 122 M{ax + 14:.1f} 122 H{ax + 46:.1f} V154" fill="none" stroke="{T["on"]}" stroke-width="7"/></g>'
    body += text("Ejaz Hussain", W - M, 214, 19, T["on"], "SemiBold", anchor="end", cls="f", style="animation-delay:.4s")
    body += text("Founder, Launch Nest Studio", W - M, 240, 16, T["on_muted"], "Regular", anchor="end", cls="f", style="animation-delay:.5s")
    style = f'''
.g{{animation:rise 1.1s {EASE} both}}
@keyframes rise{{from{{opacity:0;transform:translateY(46px)}}}}
.ul{{transform-box:fill-box;transform-origin:left;animation:hl 1.3s {EASE} both .8s}}
.arw{{animation:arw 2.6s {EASE} infinite 1.4s}}
@keyframes arw{{0%,55%,100%{{transform:translate(0,0)}}28%{{transform:translate(9px,-9px)}}}}
.wave{{transform-box:fill-box;transform-origin:center;opacity:0;animation:wave 12s cubic-bezier(.25,.6,.35,1) infinite}}
@keyframes wave{{0%{{transform:scale(.02);opacity:1}}100%{{transform:scale(1);opacity:0}}}}'''
    return doc(H, "Have a project in mind? launchnest.com.au. Ejaz Hussain, founder of Launch Nest Studio.", style, body)


PANELS = (hero, work_formaos, work_launchnest, architecture, process, stack, contact)

if __name__ == "__main__":
    for old in OUT.glob("*.svg"):
        old.unlink()
    for theme, T in THEMES.items():
        for fn in PANELS:
            save(fn.__name__.replace("_", "-"), theme, fn(T))
