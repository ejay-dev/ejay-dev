"""Builds the animated SVG panels (light + dark) for the GitHub profile README.
All type is outlined from Inter; flat colour only; one accent.
Run:  python3 scripts/build.py"""
import math
from pathlib import Path
from glyphs import text, width, wrap, glyph_x_positions, all_defs, reset

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

NAME_1, NAME_2 = "Ejaz", "Hussain"

THEMES = {
    "dark": dict(bg="#0A0A0B", panel="#131315", panel2="#1A1A1D", line="#26262A", line2="#3A3A40",
                 text="#F2F2F3", muted="#8E8E96", faint="#5A5A62",
                 accent="#2F5BFF", accent_soft="#1A2A66", on="#FFFFFF", on_muted="#C9D5FF", on_dot="#5B7FFF"),
    "light": dict(bg="#FFFFFF", panel="#F6F6F7", panel2="#EEEEF0", line="#E4E4E7", line2="#CDCDD3",
                  text="#0A0A0B", muted="#62626B", faint="#A0A0A8",
                  accent="#2F5BFF", accent_soft="#DCE4FF", on="#FFFFFF", on_muted="#D6E0FF", on_dot="#5B7FFF"),
}

W = 1000
EASE = "cubic-bezier(.16,1,.3,1)"
INOUT = "cubic-bezier(.65,0,.35,1)"
REDUCED = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"


def doc(h, label, style, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{label}">
<title>{label}</title>
<style>{style}
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
    print(f"{p.name:24s} {len(svg)/1024:6.1f} KB")


COMMON = f'''
.f{{animation:fade .9s {EASE} both}}
@keyframes fade{{from{{opacity:0;transform:translateY(10px)}}}}
.hl{{transform-box:fill-box;transform-origin:left;animation:hl 1.2s {EASE} both}}
@keyframes hl{{from{{transform:scaleX(0)}}}}
.vl{{transform-box:fill-box;transform-origin:top;animation:vl .9s {EASE} both}}
@keyframes vl{{from{{transform:scaleY(0)}}}}
.pop{{transform-box:fill-box;transform-origin:center;animation:pop .6s {EASE} both}}
@keyframes pop{{from{{opacity:0;transform:scale(0)}}}}'''


# =====================================================================
# HERO
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
CITIES = {"Adelaide": (138.6, -34.93), "Melbourne": (144.96, -37.81), "Sydney": (151.21, -33.87),
          "Brisbane": (153.03, -27.47), "Perth": (115.86, -31.95), "Darwin": (130.84, -12.46)}


def inside(pt, poly):
    x, y = pt
    c, j = False, len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            c = not c
        j = i
    return c


def hero(T):
    reset()
    H, M = 580, 52
    BX = 560  # colour block starts
    # ---- map on the accent block
    mx0, my0, mw, mh = BX + 34, 40, W - BX - 68, 380
    kx = math.cos(math.radians(27))
    lon0, lon1, lat0, lat1 = 112.9, 153.9, -10.4, -43.9
    s = min(mw / ((lon1 - lon0) * kx), mh / (lat0 - lat1))
    ox = mx0 + (mw - (lon1 - lon0) * kx * s) / 2
    proj = lambda lon, lat: (ox + (lon - lon0) * kx * s, my0 + (lat0 - lat) * s)
    inv = lambda x, y: ((x - ox) / (kx * s) + lon0, lat0 - (y - my0) / s)
    step = 9
    dots = []
    y = my0 + step / 2
    while y < my0 + mh:
        x = mx0 + step / 2
        while x < mx0 + mw:
            if inside(inv(x, y), AUS) or inside(inv(x, y), TAS):
                dots.append((x, y))
            x += step
        y += step
    snap = lambda p: min(dots, key=lambda d: (d[0] - p[0]) ** 2 + (d[1] - p[1]) ** 2)
    ax, ay = snap(proj(*CITIES["Adelaide"]))
    dot_svg = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.2" class="d" style="animation-delay:{0.5 + math.hypot(x-ax, y-ay)*0.0022:.3f}s,{2.4 + math.hypot(x-ax, y-ay)/140:.3f}s"/>'
        for x, y in dots)

    routes = ""
    for i, c in enumerate(["Perth", "Darwin", "Brisbane", "Sydney", "Melbourne"]):
        cx, cy = snap(proj(*CITIES[c]))
        dist = math.hypot(cx - ax, cy - ay)
        mxp, myp = (ax + cx) / 2, (ay + cy) / 2 - 0.3 * dist
        p = f"M{ax:.1f} {ay:.1f} Q{mxp:.1f} {myp:.1f} {cx:.1f} {cy:.1f}"
        dl = 1.7 + i * 0.18
        begin = 3.2 + i * 0.7
        routes += f'''
<path d="{p}" pathLength="1" fill="none" stroke="{T["on"]}" stroke-opacity=".55" stroke-width="1.2" class="route" style="animation-delay:{dl:.2f}s"/>
<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.6" fill="{T["on"]}" class="pop" style="animation-delay:{dl + .8:.2f}s"/>
<circle r="3" fill="{T["on"]}" opacity="0">
  <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.12;.85;1" dur="2.8s" begin="{begin:.1f}s" repeatCount="indefinite"/>
  <animateMotion path="{p}" dur="2.8s" begin="{begin:.1f}s" repeatCount="indefinite" calcMode="spline" keyPoints="0;1" keyTimes="0;1" keySplines=".45 0 .55 1"/>
</circle>'''

    # ---- left column type
    rise = lambda base: (lambda i, ch: ("g", f"animation-delay:{base + i*0.045:.3f}s"))
    name = (text(NAME_1, M - 5, 158, 124, T["text"], "Display-Bold", tracking=-0.04, per_glyph=rise(.05)) +
            text(NAME_2, M - 5, 276, 124, T["text"], "Display-Bold", tracking=-0.04, per_glyph=rise(.22)))
    assert width(NAME_2, 124, "Display-Bold", -0.04) < BX - M - 20

    lines = [("Founder of Launch Nest Studio.", T["text"])] + [
        (l, T["muted"]) for l in wrap("I design and build websites, search visibility and compliance software.", 21, BX - M - 50)]
    stmt = "".join(text(l, M, 340 + i * 31, 21, c, "Regular", cls="f", style=f"animation-delay:{.8 + i*.08:.2f}s")
                   for i, (l, c) in enumerate(lines))

    facts = ""
    cols = [("Launch Nest Studio", "Founder and CEO"), ("FormaOS", "Compliance SaaS")]
    cw = (BX - 2 * M) / 2
    for i, (a, b) in enumerate(cols):
        x = M + i * (cw + 10) + (14 if i else 0)
        facts += text(a, x, 500, 19, T["text"], "SemiBold", cls="f", style=f"animation-delay:{1.05 + i*.1:.2f}s")
        facts += text(b, x, 528, 17, T["muted"], "Regular", cls="f", style=f"animation-delay:{1.12 + i*.1:.2f}s")
    facts += f'<line x1="{M + cw + 10:.1f}" y1="474" x2="{M + cw + 10:.1f}" y2="538" stroke="{T["line"]}" class="vl" style="animation-delay:1s"/>'

    # ---- block foot
    foot = (text("Adelaide, South Australia", BX + 34, 500, 19, T["on"], "SemiBold", cls="f", style="animation-delay:1.5s") +
            text("Working with businesses Australia-wide", BX + 34, 528, 17, T["on_muted"], "Regular", cls="f", style="animation-delay:1.6s"))
    lab = text("Adelaide", ax - 14, ay + 6, 17, T["on"], "SemiBold", anchor="end", cls="f", style="animation-delay:1.5s")

    style = COMMON + f'''
.g{{animation:rise 1.2s {EASE} both}}
@keyframes rise{{from{{transform:translateY(160px)}}}}
.blk{{transform-box:fill-box;transform-origin:right;animation:blk 1.1s {EASE} both}}
@keyframes blk{{from{{transform:scaleX(0)}}}}
.d{{fill:{T["on_dot"]};transform-box:fill-box;transform-origin:center;animation:ap .7s {EASE} both,rp 7s linear infinite}}
@keyframes ap{{from{{opacity:0;transform:scale(0)}}}}
@keyframes rp{{0%{{fill:{T["on_dot"]}}}1.2%{{fill:{T["on"]}}}6%{{fill:{T["on_dot"]}}}100%{{fill:{T["on_dot"]}}}}}
.route{{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 1.3s {EASE} forwards}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
.ring{{transform-box:fill-box;transform-origin:center;animation:ring 3s cubic-bezier(.2,.6,.3,1) infinite}}
@keyframes ring{{0%{{transform:scale(.4);opacity:1}}100%{{transform:scale(3.2);opacity:0}}}}'''

    body = f'''{frame(T, H)}
<rect x="{BX}" y="1" width="{W - BX - 1}" height="{H - 2}" fill="{T["accent"]}" class="blk"/>
<clipPath id="nm"><rect x="0" y="20" width="{BX - 10}" height="276"/></clipPath>
<g clip-path="url(#nm)">{name}</g>
{stmt}
<line x1="{M}" y1="452" x2="{BX - M}" y2="452" stroke="{T["line"]}" class="hl" style="animation-delay:.95s"/>
{facts}
{dot_svg}
{routes}
<circle cx="{ax:.1f}" cy="{ay:.1f}" r="7" fill="none" stroke="{T["on"]}" stroke-width="1.5" class="ring" style="animation-delay:1.6s"/>
<circle cx="{ax:.1f}" cy="{ay:.1f}" r="7" fill="none" stroke="{T["on"]}" stroke-width="1.5" class="ring" style="animation-delay:3.1s"/>
<circle cx="{ax:.1f}" cy="{ay:.1f}" r="6.5" fill="{T["on"]}" class="pop" style="animation-delay:1.4s"/>
{lab}
<line x1="{BX + 34}" y1="452" x2="{W - 34}" y2="452" stroke="{T["on"]}" stroke-opacity=".35" class="hl" style="animation-delay:1.3s"/>
{foot}'''
    return doc(H, f"{NAME_1} {NAME_2}. Founder of Launch Nest Studio, building FormaOS. Adelaide, South Australia.", style, body)


# =====================================================================
# SEARCH
# =====================================================================
def search(T):
    reset()
    H, D, M = 540, 12, 40
    pct = lambda s: f"{s / D * 100:.2f}%"
    hold_end = 10.6

    # --- query field with typed text and caret
    q = "electrician adelaide"
    qx, qy = M + 54, 82
    xs, qw = glyph_x_positions(q, 20, "Regular")
    gcss = []
    def reveal(i, ch):
        t = (0.5 + i * 0.06) / D * 100
        gcss.append(f".t{i}{{animation:t{i} {D}s step-end infinite}}@keyframes t{i}{{0%{{opacity:0}}{t:.2f}%{{opacity:1}}100%{{opacity:1}}}}")
        return (f"t{i}", "")
    ck = ["0%{transform:translateX(0)}"] + [f"{(0.5 + i*0.06)/D*100:.2f}%{{transform:translateX({x:.1f}px)}}" for i, x in enumerate(xs)] + [f"100%{{transform:translateX({qw:.1f}px)}}"]
    field = f'''
<rect x="{M}" y="44" width="540" height="62" fill="{T["panel"]}" stroke="{T["line"]}"/>
<circle cx="{M+27}" cy="73" r="8" fill="none" stroke="{T["muted"]}" stroke-width="2"/>
<line x1="{M+33}" y1="79" x2="{M+39}" y2="85" stroke="{T["muted"]}" stroke-width="2" stroke-linecap="round"/>
<g class="lf">{text(q, qx, qy, 20, T["text"], "Regular", per_glyph=reveal)}
<rect x="{qx + 1}" y="{qy - 17}" width="2" height="23" fill="{T["accent"]}" class="caret"/></g>
<rect x="{M + 540 - 92}" y="56" width="80" height="38" fill="{T["accent"]}"/>
{text("Search", M + 540 - 52, 81, 16, T["on"], "SemiBold", anchor="middle")}'''

    # --- results
    y0, rh = 132, 76
    rx, rw = M + 46, 494
    labels = "".join(text(str(i + 1), M + 14, y0 + i * rh + 46, 22, T["faint"], "SemiBold", anchor="middle") for i in range(5))
    stages = [3.3, 4.3, 5.3, 6.3]
    comps = ["Compare quotes from local electricians", "24/7 emergency callouts, all suburbs",
             "Electrical contractors near you", "Find a licensed sparky in minutes"]

    def kf(name, moves):
        fr, cur = ["0%{transform:translateY(0)}"], 0
        for t, dy in moves:
            fr.append(f"{pct(t - .05)}{{transform:translateY({cur}px)}}")
            cur += dy
            fr.append(f"{pct(t + .65)}{{transform:translateY({cur}px)}}")
        fr.append(f"100%{{transform:translateY({cur}px)}}")
        return f"@keyframes {name}{{{''.join(fr)}}}"

    css, rows = "", ""
    for i, title in enumerate(comps):
        css += f".r{i}{{animation:r{i} {D}s {INOUT} infinite}}" + kf(f"r{i}", [(stages[3 - i], rh)])
        y = y0 + i * rh
        rows += f'''<g class="r{i}"><rect x="{rx}" y="{y + 6}" width="{rw}" height="{rh - 12}" fill="{T["bg"]}"/>
{text(title, rx + 20, y + 35, 18, T["muted"], "Medium")}
<rect x="{rx + 20}" y="{y + 48}" width="{[150,190,130,170][i]}" height="8" fill="{T["line"]}"/></g>'''
    css += f".rc{{animation:rc {D}s {INOUT} infinite}}" + kf("rc", [(t, -rh) for t in stages])
    yc = y0 + 4 * rh
    rows += f'''<g class="rc"><rect x="{rx}" y="{yc + 6}" width="{rw}" height="{rh - 12}" fill="{T["accent"]}"/>
{text("Licensed electricians in Adelaide", rx + 20, yc + 35, 18, T["on"], "SemiBold")}
{text("your-business.com.au", rx + 20, yc + 57, 15, T["on_muted"], "Medium")}
<g transform="translate({rx + rw - 40} {yc + 38})"><path d="M-8 -2 L-1 5 L10 -7" fill="none" stroke="{T["on"]}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></g></g>'''

    # --- chart card
    cx0, cy0, cwid, chei = 650, 116, 300, 300
    card = f'<rect x="{cx0 - 30}" y="44" width="{W - cx0 - 10}" height="{H - 84}" fill="{T["panel"]}" stroke="{T["line"]}"/>'
    pos = [19, 18, 18, 15, 13, 12, 9, 8, 6, 4, 3, 2, 1]
    px = lambda i: cx0 + i * cwid / (len(pos) - 1)
    py = lambda v: cy0 + (v - 1) / 19 * chei
    P = [(px(i), py(v)) for i, v in enumerate(pos)]
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in P)
    area = f"M{P[0][0]:.1f} {cy0 + chei} " + " ".join(f"L{x:.1f} {y:.1f}" for x, y in P) + f" L{P[-1][0]:.1f} {cy0 + chei} Z"
    grid = ""
    for v in (1, 5, 10, 15, 20):
        grid += f'<line x1="{cx0}" y1="{py(v):.1f}" x2="{cx0 + cwid}" y2="{py(v):.1f}" stroke="{T["line"]}"/>'
        grid += text(str(v), cx0 - 10, py(v) + 5, 14, T["faint"], "Medium", anchor="end")
    # motion head synced to the clip reveal (keyTimes by x, keyPoints by length)
    seg = [math.dist(P[i], P[i + 1]) for i in range(len(P) - 1)]
    L = sum(seg)
    cum = [0]
    for sgl in seg:
        cum.append(cum[-1] + sgl)
    t_a, t_b = 2.6 / D, 6.9 / D
    kt = ["0", f"{t_a:.4f}"] + [f"{t_a + (t_b - t_a) * (P[i][0] - P[0][0]) / cwid:.4f}" for i in range(1, len(P))] + ["1"]
    kp = ["0", "0"] + [f"{cum[i] / L:.4f}" for i in range(1, len(P))] + ["1"]
    mpath = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in P)
    chart = f'''{card}
{text("Average position", cx0 - 6, 82, 19, T["text"], "SemiBold")}
{grid}
<clipPath id="rv"><rect x="{cx0 - 2}" y="{cy0 - 20}" width="{cwid + 14}" height="{chei + 30}" class="rv"/></clipPath>
<g clip-path="url(#rv)">
  <path d="{area}" fill="{T["accent"]}" fill-opacity=".12"/>
  <polyline points="{pts}" fill="none" stroke="{T["accent"]}" stroke-width="2.5" stroke-linejoin="round"/>
</g>
<circle r="6" fill="{T["accent"]}" stroke="{T["panel"]}" stroke-width="3">
  <animateMotion path="{mpath}" dur="{D}s" repeatCount="indefinite" keyTimes="{';'.join(kt)}" keyPoints="{';'.join(kp)}" calcMode="linear"/>
</circle>
<g class="badge"><rect x="{P[-1][0] - 72}" y="{P[-1][1] - 46}" width="56" height="30" fill="{T["accent"]}"/>
{text("#1", P[-1][0] - 44, P[-1][1] - 25, 16, T["on"], "Bold", anchor="middle")}</g>
{text("Week 1", cx0, cy0 + chei + 34, 14, T["faint"], "Medium")}
{text("Week 12", cx0 + cwid, cy0 + chei + 34, 14, T["faint"], "Medium", anchor="end")}'''

    style = COMMON + f'''
{"".join(gcss)}
.caret{{animation:caret {D}s linear infinite,blink 1s steps(1) infinite}}
@keyframes caret{{{"".join(ck)}}}
@keyframes blink{{50%{{opacity:0}}}}
.lf,.rows{{animation:lf {D}s linear infinite}}
@keyframes lf{{0%{{opacity:0}}2%{{opacity:1}}{pct(hold_end)}{{opacity:1}}{pct(hold_end + .6)}{{opacity:0}}100%{{opacity:0}}}}
{css}
.rv{{transform-box:fill-box;transform-origin:left;animation:rv {D}s linear infinite}}
@keyframes rv{{0%,{pct(2.6)}{{transform:scaleX(0)}}{pct(6.9)}{{transform:scaleX(1)}}{pct(hold_end)}{{transform:scaleX(1)}}100%{{transform:scaleX(0)}}}}
.badge{{transform-box:fill-box;transform-origin:center;animation:bd {D}s {EASE} infinite}}
@keyframes bd{{0%,{pct(6.8)}{{opacity:0;transform:translateY(8px)}}{pct(7.3)}{{opacity:1;transform:translateY(0)}}{pct(hold_end)}{{opacity:1}}{pct(hold_end+.4)}{{opacity:0}}100%{{opacity:0}}}}'''
    body = f'''{frame(T, H)}
{field}
{labels}
<g class="rows">{rows}</g>
{chart}'''
    return doc(H, "Search visibility: a local business climbing from position five to position one", style, body)


# =====================================================================
# ARCHITECTURE
# =====================================================================
def icon(kind, x, y, col):
    if kind == "browser":
        return (f'<rect x="{x}" y="{y}" width="26" height="20" fill="none" stroke="{col}" stroke-width="2"/>'
                f'<line x1="{x}" y1="{y + 6}" x2="{x + 26}" y2="{y + 6}" stroke="{col}" stroke-width="2"/>')
    if kind == "phone":
        return (f'<rect x="{x + 6}" y="{y - 2}" width="15" height="24" fill="none" stroke="{col}" stroke-width="2"/>'
                f'<line x1="{x + 11}" y1="{y + 18}" x2="{x + 16}" y2="{y + 18}" stroke="{col}" stroke-width="2"/>')
    return ""


def architecture(T):
    reset()
    H = 640
    TOP = 104
    els = ""
    heads = [("CLIENTS", 40), ("APPLICATION", 310), ("DATA", 620), ("SERVICES", 40)]
    for i, (h, x) in enumerate(heads):
        y = 58 if i < 3 else 470
        els += text(h, x, y, 13, T["muted"], "SemiBold", tracking=0.12, cls="f", style=f"animation-delay:{i*.06:.2f}s")

    def box(x, y, w, h, title, sub=None, dashed=False, delay=0.0, ic=None):
        dash = ' stroke-dasharray="5 5"' if dashed else ""
        s = f'<g class="bx" style="animation-delay:{delay:.2f}s"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{T["panel"]}" stroke="{T["line2"]}"{dash}/>'
        s += text(title, x + 20, y + 35, 19, T["text"], "SemiBold")
        if sub:
            s += text(sub, x + 20, y + 59, 15, T["muted"], "Regular")
        if ic:
            s += icon(ic, x + w - 46, y + 18, T["faint"])
        return s + "</g>"

    cy = [TOP, TOP + 100, TOP + 200]
    for i, (a, b, ic) in enumerate([("Web app", "Browser", "browser"), ("iOS app", "App Store", "phone"), ("Android app", "Google Play", "phone")]):
        els += box(40, cy[i], 190, 78, a, b, delay=.1 + i * .08, ic=ic)

    ax0, aw = 310, 230
    els += box(ax0, TOP, aw, 278, "Next.js", "App Router + API", delay=.35)
    for i, t in enumerate(["Auth + sessions", "Tenant routing", "Audit logging"]):
        y = TOP + 92 + i * 58
        els += f'<g class="bx" style="animation-delay:{.45 + i*.06:.2f}s"><rect x="{ax0 + 18}" y="{y}" width="{aw - 36}" height="44" fill="{T["bg"]}" stroke="{T["line"]}"/>'
        els += f'<rect x="{ax0 + 18}" y="{y}" width="3" height="44" fill="{T["accent"]}"/>'
        els += text(t, ax0 + 36, y + 28, 15, T["text"], "Medium") + "</g>"

    dx0, dw = 620, 340
    els += box(dx0, TOP, dw, 278, "Supabase Postgres", "Row-level security per tenant", delay=.55)
    for i, t in enumerate(["NDIS provider", "Aged care", "Healthcare"]):
        y = TOP + 92 + i * 58
        els += f'<g class="bx" style="animation-delay:{.65 + i*.06:.2f}s"><rect x="{dx0 + 18}" y="{y}" width="{dw - 36}" height="44" fill="{T["bg"]}" stroke="{T["line"]}"/>'
        els += text(t, dx0 + 36, y + 28, 15, T["text"], "Medium")
        # record cells that fill in as writes land
        for k in range(6):
            cx = dx0 + 168 + k * 18
            els += f'<rect x="{cx}" y="{y + 16}" width="12" height="12" fill="{T["line"]}"/>'
            els += f'<rect x="{cx}" y="{y + 16}" width="12" height="12" fill="{T["accent"]}" class="cell" style="animation-delay:{3.0 + i*1.3 + k*0.12:.2f}s"/>'
        lx, ly = dx0 + dw - 46, y + 13
        els += f'<rect x="{lx}" y="{ly + 7}" width="14" height="11" fill="{T["muted"]}"/><path d="M{lx+3} {ly+7} v-3 a4 4 0 0 1 8 0 v3" fill="none" stroke="{T["muted"]}" stroke-width="2"/></g>'

    services = [("Stripe", "Billing", False), ("Resend", "Email", False), ("Trigger.dev", "Background jobs", False), ("Claude API", "AI features, planned", True)]
    sw, sy, bus = (920 - 60) / 4, 494, 432
    for i, (a, b, d) in enumerate(services):
        els += box(40 + i * (sw + 20), sy, sw, 96, a, b, dashed=d, delay=.8 + i * .07)

    paths = []
    for i in range(3):
        y = cy[i] + 39
        paths.append((f"M230 {y} H{ax0}", T["text"], 0.9 * i))
    paths.append((f"M{ax0 + aw} {TOP + 114} H{dx0}", T["accent"], 1.0))
    paths.append((f"M{dx0} {TOP + 230} H{ax0 + aw}", T["text"], 1.8))
    mid = ax0 + aw / 2
    for i in range(4):
        c = 40 + i * (sw + 20) + sw / 2
        sgn = 1 if c > mid else -1
        paths.append((f"M{mid} {TOP + 278} V{bus - 12} Q{mid} {bus} {mid + 12*sgn} {bus} H{c - 12*sgn:.1f} Q{c:.1f} {bus} {c:.1f} {bus + 12} V{sy}", T["accent"], 1.5 + i * .6))

    wires, packets = "", ""
    for i, (p, col, begin) in enumerate(paths):
        wires += f'<path d="{p}" pathLength="1" fill="none" stroke="{T["line2"]}" stroke-width="1.5" class="wire" style="animation-delay:{.9 + i*.05:.2f}s"/>'
        wires += f'<path d="{p}" fill="none" stroke="{T["accent"]}" stroke-width="1.5" stroke-dasharray="3 9" class="flow" style="animation-delay:{1.6 + i*.05:.2f}s"/>'
        dur = 1.5 if len(p) < 30 else 2.4
        packets += f'''<rect x="-4.5" y="-4.5" width="9" height="9" fill="{col}" opacity="0">
  <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.08;.9;1" dur="{dur}s" begin="{2.4 + begin:.2f}s" repeatCount="indefinite"/>
  <animateMotion path="{p}" dur="{dur}s" begin="{2.4 + begin:.2f}s" repeatCount="indefinite" calcMode="spline" keyPoints="0;1" keyTimes="0;1" keySplines=".5 0 .5 1"/>
</rect>'''

    style = COMMON + f'''
.bx{{animation:bx .8s {EASE} both}}
@keyframes bx{{from{{opacity:0;transform:translateY(10px)}}}}
.wire{{stroke-dasharray:1;stroke-dashoffset:1;animation:wire 1s {EASE} forwards}}
@keyframes wire{{to{{stroke-dashoffset:0}}}}
.flow{{opacity:0;animation:fl .6s ease both,march 1.2s linear infinite}}
@keyframes fl{{to{{opacity:.45}}}}
@keyframes march{{to{{stroke-dashoffset:-12}}}}
.cell{{opacity:0;animation:cell 3.9s steps(1) infinite}}
@keyframes cell{{0%{{opacity:1}}70%{{opacity:1}}71%,100%{{opacity:0}}}}'''
    return doc(H, "FormaOS architecture: web, iOS and Android clients, a Next.js app, Supabase Postgres with row-level security per tenant, and Stripe, Resend, Trigger.dev and Claude API services", style, f"{frame(T, H)}{wires}{els}{packets}")


# =====================================================================
# SHIP
# =====================================================================
def ship(T):
    reset()
    H, D = 380, 12
    pct = lambda s: f"{s / D * 100:.2f}%"
    my, x0, x1, by = 156, 60, 940, 76
    branches = [("feature/ui", 120, 300, [178, 214]), ("feature/api", 330, 520, [388, 424]), ("qa/agent-run", 550, 740, [608, 644])]
    main_nodes = [(80, "Scope", "Brief and plan"), (300, "Design", "Design system"), (520, "Build", "Next.js + Supabase"),
                  (740, "Test", "Automated QA"), (900, "Release", "Production")]
    speed = (x1 - x0) / 6.2
    t_at = lambda x: .3 + (x - x0) / speed
    t_end = t_at(x1)
    hold = D - .8
    timed = []

    def tc(kind, t_on):
        k = f"{kind}{len(timed)}"
        a, b = t_on / D * 100, min((t_on + .5) / D * 100, 99.9)
        if kind == "n":
            timed.append(f".{k}{{transform-box:fill-box;transform-origin:center;animation:{k} {D}s {EASE} infinite}}@keyframes {k}{{0%,{a:.2f}%{{transform:scale(0)}}{b:.2f}%,100%{{transform:scale(1)}}}}")
        else:
            timed.append(f".{k}{{animation:{k} {D}s {EASE} infinite}}@keyframes {k}{{0%,{a:.2f}%{{opacity:0;transform:translateY(6px)}}{b:.2f}%,100%{{opacity:1;transform:translateY(0)}}}}")
        return k

    css = (f".main{{stroke-dasharray:1;animation:mn {D}s linear infinite}}@keyframes mn{{0%{{stroke-dashoffset:1}}{pct(t_end)}{{stroke-dashoffset:0}}100%{{stroke-dashoffset:0}}}}"
           f".head{{animation:hd {D}s linear infinite}}@keyframes hd{{0%,{pct(.3)}{{transform:translateX({x0}px)}}{pct(t_end)}{{transform:translateX({x1}px)}}{pct(t_end + .3)},100%{{transform:translateX({x1}px);opacity:0}}}}")
    g = f'<path d="M{x0} {my} H{x1}" fill="none" stroke="{T["line2"]}" stroke-width="3"/>'
    g += f'<path d="M{x0} {my} H{x1}" pathLength="1" fill="none" stroke="{T["text"]}" stroke-width="3" class="main"/>'
    r = 42
    for i, (name, a, b, commits) in enumerate(branches):
        p = f"M{a} {my} C{a + r} {my} {a + r*.4} {by} {a + r + 10} {by} H{b - r - 10} C{b - r*.4} {by} {b - r} {my} {b} {my}"
        ta, tb = t_at(a), t_at(b)
        css += f".b{i}{{stroke-dasharray:1;animation:b{i} {D}s linear infinite}}@keyframes b{i}{{0%,{pct(ta)}{{stroke-dashoffset:1}}{pct(tb)}{{stroke-dashoffset:0}}100%{{stroke-dashoffset:0}}}}"
        g += f'<path d="{p}" fill="none" stroke="{T["line2"]}" stroke-width="3"/>'
        g += f'<path d="{p}" pathLength="1" fill="none" stroke="{T["accent"]}" stroke-width="3" class="b{i}"/>'
        for cx in commits:
            tcm = ta + (tb - ta) * (cx - a) / (b - a)
            g += f'<circle cx="{cx}" cy="{by}" r="7" fill="{T["bg"]}" stroke="{T["accent"]}" stroke-width="3" class="{tc("n", tcm)}"/>'
        g += text(name, a + r + 12, by - 22, 15, T["muted"], "mono", cls=tc("l", ta))
        # passing checks badge at the end of each branch
        cxp = b - r - 12
        g += f'<g class="{tc("l", tb - .35)}"><rect x="{cxp - 13}" y="{by - 13}" width="26" height="26" fill="{T["accent"]}"/><path d="M{cxp - 6} {by} L{cxp - 1} {by + 5} L{cxp + 7} {by - 5}" fill="none" stroke="{T["on"]}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></g>'
    for i, (x, t1, t2) in enumerate(main_nodes):
        tn = t_at(x)
        last = i == len(main_nodes) - 1
        g += f'<circle cx="{x}" cy="{my}" r="{10 if last else 8}" fill="{T["accent"] if last else T["bg"]}" stroke="{T["accent"] if last else T["text"]}" stroke-width="3" class="{tc("n", tn)}"/>'
        g += text(t1, x, my + 52, 20, T["text"], "SemiBold", anchor="middle", cls=tc("l", tn))
        g += text(t2, x, my + 78, 15, T["muted"], "Regular", anchor="middle", cls=tc("l", tn + .05))
    tw = width("v1.0", 15, "mono") + 26
    g += f'''<g class="{tc("l", t_at(900) + .1)}"><rect x="{900 - tw/2:.1f}" y="{my - 56}" width="{tw:.1f}" height="30" fill="{T["accent"]}"/>
<path d="M894 {my - 26} L900 {my - 19} L906 {my - 26} Z" fill="{T["accent"]}"/>{text("v1.0", 900, my - 36, 15, T["on"], "mono", anchor="middle")}</g>'''
    g += f'<circle cx="0" cy="{my}" r="6" fill="{T["accent"]}" class="head"/>'

    # deploy bar
    dy = 300
    t_dep0, t_dep1 = t_at(900), t_at(900) + 1.6
    css += (f".dep{{transform-box:fill-box;transform-origin:left;animation:dep {D}s {INOUT} infinite}}"
            f"@keyframes dep{{0%,{pct(t_dep0)}{{transform:scaleX(0)}}{pct(t_dep1)},100%{{transform:scaleX(1)}}}}")
    g += f'<rect x="40" y="{dy - 30}" width="920" height="1" fill="{T["line"]}"/>'
    g += text("Production deploy", 60, dy + 22, 17, T["text"], "SemiBold")
    bx0, bw = 260, 560
    g += f'<rect x="{bx0}" y="{dy + 9}" width="{bw}" height="10" fill="{T["panel2"]}"/>'
    g += f'<rect x="{bx0}" y="{dy + 9}" width="{bw}" height="10" fill="{T["accent"]}" class="dep"/>'
    live = tc("l", t_dep1)
    g += f'<g class="{live}"><circle cx="{bx0 + bw + 30}" cy="{dy + 14}" r="6" fill="{T["accent"]}"/>{text("Live", bx0 + bw + 46, dy + 20, 17, T["text"], "SemiBold")}</g>'

    style = f'''{css}
{"".join(timed)}
.all{{animation:all {D}s linear infinite}}
@keyframes all{{0%,{pct(hold)}{{opacity:1}}100%{{opacity:0}}}}'''
    return doc(H, "How I ship: scope, design, build, automated QA, production release", style, f'{frame(T, H)}<g class="all">{g}</g>')


# =====================================================================
# STACK
# =====================================================================
def stack(T):
    reset()
    blocks = [("Frontend", [("Next.js", "App Router"), ("React", "Server Components"), ("TypeScript", "Strict mode"),
                            ("Tailwind CSS", "Design tokens"), ("shadcn/ui", "Component system")]),
              ("Backend", [("Supabase", "Postgres + Auth"), ("Row-level security", "Tenant isolation"), ("Stripe", "Billing"),
                           ("Resend", "Transactional email"), ("Trigger.dev", "Background jobs")]),
              ("Platform", [("Vercel", "Hosting + edge"), ("iOS + Android", "Mobile apps"), ("WordPress", "Client sites"),
                            ("Figma", "Product design"), ("GitHub", "Source + CI")]),
              ("Search + AI", [("Technical SEO", "Core Web Vitals"), ("AEO", "Answer engines"), ("GEO", "Generative search"),
                               ("Claude Code", "Development"), ("Claude API", "In-app AI")])]
    M, G = 40, 40
    bw = (W - 2 * M - G) / 2
    rh, top = 46, 64
    bh = 24 + 5 * rh
    H = top + 2 * bh + 70 + 24
    D = 10
    body = frame(T, H)
    n = 0
    for bi, (head, items) in enumerate(blocks):
        x = M + (bi % 2) * (bw + G)
        y = top + (bi // 2) * (bh + 70)
        dl = bi * .12
        body += text(head.upper(), x, y, 13, T["muted"], "SemiBold", tracking=.12, cls="f", style=f"animation-delay:{dl:.2f}s")
        body += f'<rect x="{x}" y="{y + 16}" width="{bw:.1f}" height="2" fill="{T["text"]}" class="hl" style="animation-delay:{dl + .1:.2f}s"/>'
        for r, (a, b) in enumerate(items):
            yy = y + 18 + (r + 1) * rh
            d = .3 + dl + r * .06
            body += f'<g class="f" style="animation-delay:{d:.2f}s">'
            body += f'<rect x="{x}" y="{yy - rh + 1}" width="4" height="{rh - 2}" fill="{T["accent"]}" class="sw" style="animation-delay:{2 + n*D/20:.2f}s"/>'
            body += f'<rect x="{x}" y="{yy - rh + 1}" width="{bw:.1f}" height="{rh - 2}" fill="{T["accent"]}" class="sb" style="animation-delay:{2 + n*D/20:.2f}s"/>'
            body += text(a, x + 16, yy - 16, 18, T["text"], "Medium")
            body += text(b, x + bw - 4, yy - 16, 16, T["muted"], "Regular", anchor="end")
            body += f'<line x1="{x}" y1="{yy}" x2="{x + bw:.1f}" y2="{yy}" stroke="{T["line"]}"/></g>'
            n += 1
    style = COMMON + f'''
.sw{{opacity:0;animation:sw {D}s ease-out infinite}}
@keyframes sw{{0%{{opacity:1}}8%{{opacity:0}}100%{{opacity:0}}}}
.sb{{opacity:0;animation:sb {D}s ease-out infinite}}
@keyframes sb{{0%{{opacity:.1}}8%{{opacity:0}}100%{{opacity:0}}}}'''
    return doc(H, "Stack: Next.js, React, TypeScript, Tailwind CSS, shadcn/ui, Supabase, Stripe, Resend, Trigger.dev, Vercel, iOS, Android, WordPress, Figma, GitHub, SEO, AEO, GEO, Claude Code, Claude API", style, body)


# =====================================================================
# CONTACT
# =====================================================================
def contact(T):
    reset()
    H, M = 280, 52
    url = "launchnest.com.au"
    uw = width(url, 78, "Display-SemiBold", tracking=-.025)
    body = frame(T, H, T["accent"])
    body += text("Have a project in mind?", M, 82, 22, T["on_muted"], "Regular", cls="f")
    body += text(url, M - 3, 172, 78, T["on"], "Display-SemiBold", tracking=-.025,
                 per_glyph=lambda i, ch: ("g", f"animation-delay:{.15 + i*.03:.2f}s"))
    body += f'<rect x="{M}" y="196" width="{uw:.1f}" height="4" fill="{T["on"]}" class="ul"/>'
    ax = M + uw + 30
    body += f'<g class="arw"><path d="M{ax + 6:.1f} {162} L{ax + 46:.1f} {122} M{ax + 14:.1f} {122} H{ax + 46:.1f} V{154}" fill="none" stroke="{T["on"]}" stroke-width="7"/></g>'
    rx = W - M
    body += text(f"{NAME_1} {NAME_2}", rx, 214, 19, T["on"], "SemiBold", anchor="end", cls="f", style="animation-delay:.4s")
    body += text("Founder, Launch Nest Studio", rx, 240, 16, T["on_muted"], "Regular", anchor="end", cls="f", style="animation-delay:.5s")
    style = COMMON + f'''
.g{{animation:rise 1.1s {EASE} both}}
@keyframes rise{{from{{opacity:0;transform:translateY(46px)}}}}
.ul{{transform-box:fill-box;transform-origin:left;animation:hl 1.3s {EASE} both .8s}}
.arw{{animation:arw 2.6s {EASE} infinite 1.4s}}
@keyframes arw{{0%,55%,100%{{transform:translate(0,0)}}28%{{transform:translate(9px,-9px)}}}}'''
    return doc(H, f"Have a project in mind? launchnest.com.au. {NAME_1} {NAME_2}, founder of Launch Nest Studio.", style, body)


if __name__ == "__main__":
    for theme, T in THEMES.items():
        for fn in (hero, search, architecture, ship, stack, contact):
            save(fn.__name__, theme, fn(T))
