"""Builds the animated SVG panels (light + dark) for Ejaz's GitHub profile README.
All type is outlined from Inter; flat colour only; single accent."""
import math
import random
from pathlib import Path
from glyphs import text, width, wrap, glyph_x_positions, all_defs, reset

OUT = Path(__file__).resolve().parent.parent / "assets"
OUT.mkdir(exist_ok=True)

THEMES = {
    "dark": dict(bg="#0A0A0A", panel="#121212", line="#262626", line2="#3A3A3A", dot="#383838",
                 text="#EDEDED", muted="#8F8F8F", accent="#3D6DFF", onaccent="#FFFFFF"),
    "light": dict(bg="#FFFFFF", panel="#F6F6F6", line="#E5E5E5", line2="#CFCFCF", dot="#DCDCDC",
                  text="#0A0A0A", muted="#6A6A6A", accent="#2250F4", onaccent="#FFFFFF"),
}

W = 1000
EASE = "cubic-bezier(.16,1,.3,1)"  # expo-out
REDUCED = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"


def svg_doc(name, h, label, style, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{label}">
<title>{label}</title>
<style>{style}
{REDUCED}</style>
{all_defs()}
{body}
</svg>
'''


def frame(T, h):
    return f'<rect x="0.5" y="0.5" width="{W-1}" height="{h-1}" fill="{T["bg"]}" stroke="{T["line"]}"/>'


def save(name, theme, svg):
    p = OUT / f"{name}-{theme}.svg"
    p.write_text(svg)
    print(f"{p.name:24s} {len(svg)/1024:6.1f} KB")


# =====================================================================
# HERO — name, statement, dot-matrix Australia radiating from Adelaide
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
          "Brisbane": (153.03, -27.47), "Perth": (115.86, -31.95)}


def inside(pt, poly):
    x, y = pt
    c = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            c = not c
        j = i
    return c


def hero(T):
    reset()
    H = 560
    M = 48
    # map box
    mx0, my0, mw, mh = 548, 44, 410, 360
    kx = math.cos(math.radians(27))
    lon0, lon1, lat0, lat1 = 112.9, 153.9, -10.4, -43.9
    s = min(mw / ((lon1 - lon0) * kx), mh / (lat0 - lat1))
    ox = mx0 + (mw - (lon1 - lon0) * kx * s) / 2
    proj = lambda lon, lat: (ox + (lon - lon0) * kx * s, my0 + (lat0 - lat) * s)
    inv = lambda x, y: ((x - ox) / (kx * s) + lon0, lat0 - (y - my0) / s)
    ax, ay = proj(*CITIES["Adelaide"])

    step = 9.5
    dots = []
    y = my0 + step / 2
    while y < my0 + mh:
        x = mx0 + step / 2
        while x < mx0 + mw:
            ll = inv(x, y)
            if inside(ll, AUS) or inside(ll, TAS):
                dots.append((x, y))
            x += step
        y += step
    # snap Adelaide to nearest dot
    ax, ay = min(dots, key=lambda d: (d[0] - ax) ** 2 + (d[1] - ay) ** 2)
    dot_svg = []
    for x, y in dots:
        d = math.hypot(x - ax, y - ay)
        dot_svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.3" class="d" style="animation-delay:{0.35 + d*0.0024:.3f}s,{2.2 + d/150:.3f}s"/>')

    # routes from Adelaide
    routes = ""
    for i, c in enumerate(["Perth", "Melbourne", "Sydney", "Brisbane"]):
        cx, cy = proj(*CITIES[c])
        cx, cy = min(dots, key=lambda d: (d[0] - cx) ** 2 + (d[1] - cy) ** 2)
        mxp, myp = (ax + cx) / 2, (ay + cy) / 2 - 0.28 * math.hypot(cx - ax, cy - ay)
        p = f"M{ax:.1f} {ay:.1f} Q{mxp:.1f} {myp:.1f} {cx:.1f} {cy:.1f}"
        dl = 1.6 + i * 0.25
        routes += f'''
  <path d="{p}" pathLength="1" fill="none" stroke="{T["text"]}" stroke-width="1.25" class="route" style="animation-delay:{dl:.2f}s"/>
  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="4" fill="{T["text"]}" class="pop" style="animation-delay:{dl + 0.7:.2f}s"/>
  <rect x="-3.5" y="-3.5" width="7" height="7" fill="{T["accent"]}" opacity="0">
    <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.1;0.85;1" dur="3.2s" begin="{3 + i*0.8:.1f}s" repeatCount="indefinite"/>
    <animateMotion path="{p}" dur="3.2s" begin="{3 + i*0.8:.1f}s" repeatCount="indefinite" keyPoints="0;1" keyTimes="0;1" calcMode="spline" keySplines=".45 0 .55 1"/>
  </rect>'''

    # name — each glyph rises from a mask
    rise = lambda i, ch: ("g", f"animation-delay:{0.05 + i*0.045:.3f}s")
    name1 = text("Ejaz", M - 4, 152, 128, T["text"], "Display-Bold", tracking=-0.035, per_glyph=rise)
    name2 = text("Hussaini", M - 4, 268, 128, T["text"], "Display-Bold", tracking=-0.035,
                 per_glyph=lambda i, ch: ("g", f"animation-delay:{0.25 + i*0.045:.3f}s"))

    lines = [("Founder of Launch Nest Studio.", T["text"])] + [
        (l, T["muted"]) for l in wrap("I build websites, search visibility and compliance software for Australian businesses.", 22, 492, "Regular")]
    stmt_svg = "".join(
        text(l, M, 334 + i * 32, 22, c, "Regular", cls="f", style=f"animation-delay:{0.75 + i*0.08:.2f}s")
        for i, (l, c) in enumerate(lines)
    )

    # Adelaide label
    lab = text("Adelaide", ax - 14, ay + 6, 18, T["text"], "SemiBold", anchor="end", cls="f", style="animation-delay:1.4s")

    # bottom facts row
    cols = [("Launch Nest Studio", "Founder. Web, brand, search."),
            ("FormaOS", "Multi-tenant compliance SaaS."),
            ("AI-native", "Agent-built, production-grade.")]
    cw = (W - 2 * M) / 3
    facts = ""
    for i, (t1, t2) in enumerate(cols):
        x = M + i * cw + (0 if i == 0 else 24)
        facts += text(t1, x, 486, 20, T["text"], "SemiBold", cls="f", style=f"animation-delay:{1.0 + i*0.1:.2f}s")
        assert width(t2, 18) < cw - 32, t2
        facts += text(t2, x, 516, 18, T["muted"], "Regular", cls="f", style=f"animation-delay:{1.08 + i*0.1:.2f}s")
        if i:
            facts += f'<line x1="{M + i*cw:.1f}" y1="458" x2="{M + i*cw:.1f}" y2="524" stroke="{T["line"]}" class="vl" style="animation-delay:{0.95 + i*0.1:.2f}s"/>'

    style = f'''
.g{{animation:rise 1.1s {EASE} both}}
@keyframes rise{{from{{transform:translateY(150px)}}}}
.f{{animation:fade .9s {EASE} both}}
@keyframes fade{{from{{opacity:0;transform:translateY(10px)}}}}
.d{{fill:{T["dot"]};transform-box:fill-box;transform-origin:center;animation:ap .6s {EASE} both,rp 6s linear infinite}}
@keyframes ap{{from{{opacity:0;transform:scale(0)}}}}
@keyframes rp{{0%{{fill:{T["dot"]}}}1%{{fill:{T["accent"]}}}5%{{fill:{T["dot"]}}}100%{{fill:{T["dot"]}}}}}
.route{{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 1.2s {EASE} forwards}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
.pop{{transform-box:fill-box;transform-origin:center;animation:ap .5s {EASE} both}}
.hl{{transform-box:fill-box;transform-origin:left;animation:hl 1.2s {EASE} both;animation-delay:.9s}}
@keyframes hl{{from{{transform:scaleX(0)}}}}
.vl{{transform-box:fill-box;transform-origin:top;animation:vl .8s {EASE} both}}
@keyframes vl{{from{{transform:scaleY(0)}}}}
.ring{{transform-box:fill-box;transform-origin:center;animation:ring 3s ease-out infinite}}
@keyframes ring{{0%{{transform:scale(.3);opacity:1}}100%{{transform:scale(2.6);opacity:0}}}}'''

    body = f'''{frame(T, H)}
<clipPath id="nm"><rect x="0" y="20" width="540" height="270"/></clipPath>
<g clip-path="url(#nm)">{name1}{name2}</g>
{stmt_svg}
{"".join(dot_svg)}
{routes}
<circle cx="{ax:.1f}" cy="{ay:.1f}" r="7" fill="none" stroke="{T["accent"]}" stroke-width="1.5" class="ring" style="animation-delay:1.4s"/>
<circle cx="{ax:.1f}" cy="{ay:.1f}" r="7" fill="none" stroke="{T["accent"]}" stroke-width="1.5" class="ring" style="animation-delay:2.9s"/>
<circle cx="{ax:.1f}" cy="{ay:.1f}" r="6" fill="{T["accent"]}" class="pop" style="animation-delay:1.2s"/>
{lab}
<line x1="{M}" y1="436" x2="{W-M}" y2="436" stroke="{T["line"]}" class="hl"/>
{facts}'''
    return svg_doc("hero", H, "Ejaz Hussaini. Founder of Launch Nest Studio, building FormaOS. Adelaide, Australia.", style, body)


# =====================================================================
# SEARCH — query types, client climbs to position 1, chart draws
# =====================================================================
def search(T):
    reset()
    H = 500
    D = 12  # loop seconds
    pct = lambda s: f"{s / D * 100:.2f}%"
    M = 40
    # search field
    q = "electrician adelaide"
    qx, qy = M + 52, 78
    xs, qw = glyph_x_positions(q, 20, "Regular")
    glyph_css = []
    def glyph_reveal(i, ch):
        t = (0.4 + i * 0.055) / D * 100
        glyph_css.append(f".t{i}{{animation:t{i} {D}s step-end infinite}}@keyframes t{i}{{0%{{opacity:0}}{t:.2f}%{{opacity:1}}100%{{opacity:1}}}}")
        return (f"t{i}", "")
    # caret keyframes follow glyph positions while typing, then idle blink
    caret_kf = []
    t0, dt = 0.4, 0.055
    caret_kf.append(f"0%{{transform:translateX(0)}}")
    for i, x in enumerate(xs):
        caret_kf.append(f"{(t0 + i*dt)/D*100:.2f}%{{transform:translateX({x:.1f}px)}}")
    caret_kf.append(f"100%{{transform:translateX({qw:.1f}px)}}")

    field = f'''
<rect x="{M}" y="{40}" width="540" height="58" fill="{T["panel"]}" stroke="{T["line"]}"/>
<circle cx="{M+26}" cy="68" r="8" fill="none" stroke="{T["muted"]}" stroke-width="2"/>
<line x1="{M+32}" y1="74" x2="{M+38}" y2="80" stroke="{T["muted"]}" stroke-width="2" stroke-linecap="round"/>
<g class="loopfade">{text(q, qx, qy + 2, 20, T["text"], "Regular", per_glyph=glyph_reveal)}
<rect x="{qx + 1}" y="{qy - 16}" width="2" height="22" fill="{T["accent"]}" class="caret"/></g>'''

    # result rows
    rows_y0, rh = 126, 70
    labels = ""
    for i in range(5):
        labels += text(str(i + 1), M + 14, rows_y0 + i * rh + 42, 22, T["muted"], "SemiBold", anchor="middle")
    rx, rw = M + 44, 496
    # stage times (s) where the client passes a row
    stages = [3.2, 4.2, 5.2, 6.2]
    hold_end = 10.6

    def row_kf(name, moves):
        """moves: list of (time, from_idx, to_idx)."""
        frames = [f"0%{{transform:translateY(0)}}"]
        cur = 0
        for t, dy in moves:
            frames.append(f"{pct(t - 0.05)}{{transform:translateY({cur}px)}}")
            cur += dy
            frames.append(f"{pct(t + 0.6)}{{transform:translateY({cur}px)}}")
        frames.append(f"100%{{transform:translateY({cur}px)}}")
        return f"@keyframes {name}{{{''.join(frames)}}}"

    css_rows = ""
    rows = ""
    widths = [(300, 200), (260, 230), (330, 180), (280, 210)]
    for i in range(4):  # competitors start at idx 0..3; competitor i is passed at stage 3-i
        t = stages[3 - i]
        css_rows += f".r{i}{{animation:r{i} {D}s cubic-bezier(.65,0,.35,1) infinite}}" + row_kf(f"r{i}", [(t, rh)])
        y = rows_y0 + i * rh
        a, b = widths[i]
        rows += f'''<g class="r{i}">
  <rect x="{rx}" y="{y + 6}" width="{rw}" height="{rh - 12}" fill="{T["bg"]}"/>
  <rect x="{rx + 18}" y="{y + 19}" width="{a}" height="12" fill="{T["line2"]}"/>
  <rect x="{rx + 18}" y="{y + 40}" width="{b}" height="9" fill="{T["line"]}"/>
</g>'''
    css_rows += f".rc{{animation:rc {D}s cubic-bezier(.65,0,.35,1) infinite}}" + row_kf("rc", [(t, -rh) for t in stages])
    yc = rows_y0 + 4 * rh
    rows += f'''<g class="rc">
  <rect x="{rx}" y="{yc + 6}" width="{rw}" height="{rh - 12}" fill="{T["panel"]}" stroke="{T["line"]}"/>
  <rect x="{rx}" y="{yc + 6}" width="4" height="{rh - 12}" fill="{T["accent"]}"/>
  {text("Licensed electricians in Adelaide", rx + 20, yc + 33, 19, T["text"], "SemiBold")}
  {text("your-business.com.au", rx + 20, yc + 55, 16, T["accent"], "Medium")}
</g>'''

    # chart
    cx0, cy0, cwid, chei = 640, 60, 320, 330
    pos = [19, 18, 18, 15, 13, 12, 9, 8, 6, 4, 3, 2, 1]
    px = lambda i: cx0 + i * cwid / (len(pos) - 1)
    py = lambda v: cy0 + (v - 1) / 19 * chei
    pts = " ".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(pos))
    grid = ""
    for v in (1, 5, 10, 15, 20):
        grid += f'<line x1="{cx0}" y1="{py(v):.1f}" x2="{cx0 + cwid}" y2="{py(v):.1f}" stroke="{T["line"]}"/>'
        grid += text(str(v), cx0 - 12, py(v) + 6, 16, T["muted"], "Medium", anchor="end")
    chart = f'''{grid}
{text("Week 1", cx0, cy0 + chei + 40, 16, T["muted"], "Medium")}
{text("Week 12", cx0 + cwid, cy0 + chei + 40, 16, T["muted"], "Medium", anchor="end")}
{text("Average position", cx0, cy0 - 24, 18, T["text"], "SemiBold")}
<polyline points="{pts}" pathLength="1" fill="none" stroke="{T["accent"]}" stroke-width="2.5" stroke-linejoin="round" class="line"/>
<g class="end"><circle cx="{px(12):.1f}" cy="{py(1):.1f}" r="6" fill="{T["accent"]}"/></g>'''

    style = f'''
{"".join(glyph_css)}
.caret{{animation:caret {D}s linear infinite,blink 1s steps(1) infinite}}
@keyframes caret{{{"".join(caret_kf)}}}
@keyframes blink{{50%{{opacity:0}}}}
.loopfade,.rows,.cl{{animation:lf {D}s linear infinite}}
@keyframes lf{{0%{{opacity:0}}2%{{opacity:1}}{pct(hold_end)}{{opacity:1}}{pct(hold_end + 0.6)}{{opacity:0}}100%{{opacity:0}}}}
{css_rows}
.line{{stroke-dasharray:1;animation:ln {D}s linear infinite}}
@keyframes ln{{0%,{pct(2.6)}{{stroke-dashoffset:1}}{pct(6.9)}{{stroke-dashoffset:0}}100%{{stroke-dashoffset:0}}}}
.end{{transform-box:fill-box;transform-origin:center;animation:end {D}s {EASE} infinite}}
@keyframes end{{0%,{pct(6.8)}{{transform:scale(0)}}{pct(7.3)}{{transform:scale(1)}}100%{{transform:scale(1)}}}}'''
    # glyph reveal: each glyph hidden until its delay, within each loop. Use per-glyph delay on a loop-length animation.
    style = style.replace(".t{opacity:0;animation:t", ".t{opacity:0;animation:t")
    body = f'''{frame(T, H)}
{field}
{labels}
<g class="rows">{rows}</g>
<g class="cl">{chart}</g>'''
    return svg_doc("search", H, "Search visibility: a local business climbing from position five to position one", style, body)


# =====================================================================
# ARCHITECTURE — FormaOS system diagram with live data flow
# =====================================================================
def architecture(T):
    reset()
    H = 580

    def box(x, y, w, h, title, sub=None, dashed=False, fill=None, delay=0):
        dash = ' stroke-dasharray="5 5"' if dashed else ""
        s = f'<g class="bx" style="animation-delay:{delay:.2f}s"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill or T["panel"]}" stroke="{T["line2"]}"{dash}/>'
        s += text(title, x + 18, y + 34, 19, T["text"], "SemiBold")
        if sub:
            s += text(sub, x + 18, y + 58, 16, T["muted"], "Regular")
        return s + "</g>"

    els = ""
    # clients
    clients = [("Web app", "Browser"), ("iOS app", "App Store"), ("Android app", "Google Play")]
    cy = [70, 172, 274]
    for i, (a, b) in enumerate(clients):
        els += box(40, cy[i], 180, 76, a, b, delay=0.1 + i * 0.08)
    # app
    els += box(310, 70, 220, 280, "Next.js", "App Router + API", delay=0.35)
    app_inner = ["Auth + sessions", "Tenant routing", "Audit logging"]
    for i, t in enumerate(app_inner):
        y = 160 + i * 56
        els += f'<g class="bx" style="animation-delay:{0.45 + i*0.06:.2f}s"><rect x="328" y="{y}" width="184" height="42" fill="{T["bg"]}" stroke="{T["line"]}"/>'
        els += text(t, 344, y + 27, 16, T["text"], "Medium") + "</g>"
    # database
    els += box(620, 70, 340, 280, "Supabase Postgres", "Row-level security per tenant", delay=0.55)
    tenants = ["NDIS provider", "Aged care", "Healthcare"]
    for i, t in enumerate(tenants):
        y = 160 + i * 56
        els += f'<g class="bx" style="animation-delay:{0.65 + i*0.06:.2f}s"><rect x="638" y="{y}" width="304" height="42" fill="{T["bg"]}" stroke="{T["line"]}"/>'
        els += f'<rect x="638" y="{y}" width="304" height="42" fill="{T["accent"]}" class="hit" style="animation-delay:{3.1 + i*1.6:.2f}s"/>'
        els += text(t, 656, y + 27, 16, T["text"], "Medium")
        # padlock
        lx, ly = 914, y + 14
        els += f'<rect x="{lx}" y="{ly + 6}" width="14" height="11" fill="{T["muted"]}"/><path d="M{lx+3} {ly+6} v-3 a4 4 0 0 1 8 0 v3" fill="none" stroke="{T["muted"]}" stroke-width="2"/>'
        els += "</g>"
    # services bus
    services = [("Stripe", "Billing", False), ("Resend", "Email", False), ("Trigger.dev", "Background jobs", False), ("Claude API", "AI features, planned", True)]
    sw = (920 - 3 * 20) / 4
    sy = 450
    bus_y = 410
    for i, (a, b, dashed) in enumerate(services):
        x = 40 + i * (sw + 20)
        els += box(x, sy, sw, 86, a, b, dashed=dashed, delay=0.8 + i * 0.07)

    # connectors
    paths = []
    for i in range(3):
        y = cy[i] + 38
        paths.append((f"M220 {y} H310", "fwd", 0.0 + i * 0.9))
    paths.append(("M530 181 H620", "fwd", 1.2))
    paths.append(("M620 239 H530", "back", 2.0))
    centers = [40 + i * (sw + 20) + sw / 2 for i in range(4)]
    for i, c in enumerate(centers):
        paths.append((f"M420 350 V{bus_y - 12} Q420 {bus_y} {420 + (12 if c > 420 else -12)} {bus_y} H{c + (-12 if c > 420 else 12):.1f} Q{c:.1f} {bus_y} {c:.1f} {bus_y + 12} V{sy}", "fwd", 1.6 + i * 0.7))

    lines = ""
    packets = ""
    for i, (p, kind, begin) in enumerate(paths):
        lines += f'<path d="{p}" pathLength="1" fill="none" stroke="{T["line2"]}" stroke-width="1.5" class="wire" style="animation-delay:{0.9 + i*0.05:.2f}s"/>'
        col = T["accent"] if kind == "fwd" else T["text"]
        dur = 1.4 if len(p) < 30 else 2.2
        packets += f'''<rect x="-4" y="-4" width="8" height="8" fill="{col}" opacity="0">
  <animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.08;0.92;1" dur="{dur}s" begin="{2.4 + begin:.2f}s" repeatCount="indefinite"/>
  <animateMotion path="{p}" dur="{dur}s" begin="{2.4 + begin:.2f}s" repeatCount="indefinite" calcMode="spline" keyPoints="0;1" keyTimes="0;1" keySplines=".5 0 .5 1"/>
</rect>'''
        # repeat interval is dur; stagger via begin only — acceptable continuous flow

    style = f'''
.bx{{animation:bx .8s {EASE} both}}
@keyframes bx{{from{{opacity:0;transform:translateY(8px)}}}}
.wire{{stroke-dasharray:1;stroke-dashoffset:1;animation:wire 1s {EASE} forwards}}
@keyframes wire{{to{{stroke-dashoffset:0}}}}
.hit{{opacity:0;animation:hit 4.8s ease-out infinite}}
@keyframes hit{{0%{{opacity:.28}}25%{{opacity:0}}100%{{opacity:0}}}}'''
    body = f'''{frame(T, H)}
{lines}
{els}
{packets}'''
    return svg_doc("architecture", H, "FormaOS architecture: web, iOS and Android clients, Next.js app, Supabase Postgres with row-level security per tenant, and Stripe, Resend, Trigger.dev and Claude API services", style, body)


# =====================================================================
# SHIP — git graph of a release
# =====================================================================
def ship(T):
    reset()
    H = 300
    D = 11
    pct = lambda s: f"{s / D * 100:.2f}%"
    my = 150
    x0, x1 = 60, 940
    branch_y = 70
    branches = [("feature/ui", 120, 300, [175, 235]),
                ("feature/api", 330, 520, [385, 455]),
                ("qa/agent-run", 550, 740, [605, 675])]
    main_nodes = [(80, "Scope", "Brief and plan"), (300, "Design", "Design system"), (520, "Build", "Next.js + Supabase"),
                  (740, "Test", "Agent QA run"), (900, "Release", "Live")]
    speed = (x1 - x0) / 6.0  # px per second for the main line
    t_at = lambda x: 0.3 + (x - x0) / speed

    timed = []
    def tcls(kind, t_on):
        k = f"{kind}{len(timed)}"
        a, b = t_on / D * 100, min((t_on + 0.5) / D * 100, 99.9)
        if kind == "n":
            timed.append(f".{k}{{transform-box:fill-box;transform-origin:center;animation:{k} {D}s {EASE} infinite}}"
                         f"@keyframes {k}{{0%,{a:.2f}%{{transform:scale(0)}}{b:.2f}%,100%{{transform:scale(1)}}}}")
        else:
            timed.append(f".{k}{{animation:{k} {D}s {EASE} infinite}}"
                         f"@keyframes {k}{{0%,{a:.2f}%{{opacity:0;transform:translateY(6px)}}{b:.2f}%,100%{{opacity:1;transform:translateY(0)}}}}")
        return k

    css = f".main{{stroke-dasharray:1;animation:mn {D}s linear infinite}}@keyframes mn{{0%{{stroke-dashoffset:1}}{pct(t_at(x1))}{{stroke-dashoffset:0}}100%{{stroke-dashoffset:0}}}}"
    body = f'<path d="M{x0} {my} H{x1}" pathLength="1" fill="none" stroke="{T["line2"]}" stroke-width="2"/>'
    body += f'<path d="M{x0} {my} H{x1}" pathLength="1" fill="none" stroke="{T["text"]}" stroke-width="2" class="main"/>'
    r = 40
    for i, (name, a, b, commits) in enumerate(branches):
        p = (f"M{a} {my} C{a + r} {my} {a + r*0.4} {branch_y} {a + r + 10} {branch_y} "
             f"H{b - r - 10} C{b - r*0.4} {branch_y} {b - r} {my} {b} {my}")
        ta, tb = t_at(a), t_at(b)
        css += (f".b{i}{{stroke-dasharray:1;animation:b{i} {D}s linear infinite}}"
                f"@keyframes b{i}{{0%,{pct(ta)}{{stroke-dashoffset:1}}{pct(tb)}{{stroke-dashoffset:0}}100%{{stroke-dashoffset:0}}}}")
        body += f'<path d="{p}" pathLength="1" fill="none" stroke="{T["line2"]}" stroke-width="2"/>'
        body += f'<path d="{p}" pathLength="1" fill="none" stroke="{T["accent"]}" stroke-width="2" class="b{i}"/>'
        for j, cx in enumerate(commits):
            tc = ta + (tb - ta) * (cx - a) / (b - a)
            body += f'<circle cx="{cx}" cy="{branch_y}" r="6" fill="{T["bg"]}" stroke="{T["accent"]}" stroke-width="2" class="{tcls('n', tc)}"/>'
        body += text(name, a + r + 12, branch_y - 20, 16, T["muted"], "mono", cls=tcls("l", ta))
    for i, (x, t1, t2) in enumerate(main_nodes):
        tn = t_at(x)
        last = i == len(main_nodes) - 1
        fill = T["accent"] if last else T["bg"]
        stroke = T["accent"] if last else T["text"]
        body += f'<circle cx="{x}" cy="{my}" r="{9 if last else 7}" fill="{fill}" stroke="{stroke}" stroke-width="2" class="{tcls('n', tn)}"/>'
        body += text(t1, x, my + 50, 20, T["text"], "SemiBold", anchor="middle", cls=tcls("l", tn))
        body += text(t2, x, my + 76, 16, T["muted"], "Regular", anchor="middle", cls=tcls("l", tn + 0.05))
    # release tag
    tx = 900
    tw = width("v1.0", 16, "mono") + 24
    body += f'''<g class="{tcls('l', t_at(tx) + 0.1)}">
  <rect x="{tx - tw/2:.1f}" y="{my - 52}" width="{tw:.1f}" height="28" fill="{T["accent"]}"/>
  <path d="M{tx - 6} {my - 24} L{tx} {my - 17} L{tx + 6} {my - 24} Z" fill="{T["accent"]}"/>
  {text("v1.0", tx, my - 33, 16, T["onaccent"], "mono", anchor="middle")}
</g>'''
    hold = pct(D - 0.8)
    style = f'''{css}
{"".join(timed)}
.all{{animation:all {D}s linear infinite}}
@keyframes all{{0%,{hold}{{opacity:1}}100%{{opacity:0}}}}'''
    # per-element delays shift the whole loop: the n/lb keyframes start at their own delay, which keeps
    # nodes in sync with the line on every loop because all animations share the same duration.
    body = f'{frame(T, H)}<g class="all">{body}</g>'
    return svg_doc("ship", H, "How I ship: scope, design, build, agent QA, release", style, body)


# =====================================================================
# STACK — typographic table
# =====================================================================
def stack(T):
    reset()
    cols = [("Frontend", ["Next.js", "React", "TypeScript", "Tailwind CSS", "shadcn/ui"]),
            ("Backend", ["Supabase", "PostgreSQL + RLS", "Stripe", "Resend", "Trigger.dev"]),
            ("Platform", ["Vercel", "iOS + Android", "WordPress", "Figma", "GitHub"]),
            ("AI + Search", ["Claude Code", "Claude API", "Technical SEO", "AEO", "GEO"])]
    M = 40
    cw = (W - 2 * M) / 4
    top, rh = 64, 48
    H = top + 24 + rh * 5 + 36
    body = frame(T, H)
    D = 10
    n = 0
    for c, (head, items) in enumerate(cols):
        x = M + c * cw
        body += text(head.upper(), x, top, 15, T["muted"], "SemiBold", tracking=0.08, cls="f", style=f"animation-delay:{c*0.08:.2f}s")
        body += f'<line x1="{x}" y1="{top + 18}" x2="{x + cw - 24}" y2="{top + 18}" stroke="{T["text"]}" stroke-width="1.5" class="hl" style="animation-delay:{0.1 + c*0.08:.2f}s"/>'
        for r, item in enumerate(items):
            y = top + 18 + (r + 1) * rh
            d = 0.3 + c * 0.08 + r * 0.06
            body += f'<g class="f" style="animation-delay:{d:.2f}s">'
            body += f'<rect x="{x}" y="{y - rh + 1}" width="{cw - 24}" height="{rh - 1}" fill="{T["accent"]}" class="sw" style="animation-delay:{2 + n*D/20:.2f}s"/>'
            body += text(item, x, y - 16, 19, T["text"], "Medium")
            body += f'<line x1="{x}" y1="{y}" x2="{x + cw - 24}" y2="{y}" stroke="{T["line"]}"/></g>'
            n += 1
    style = f'''
.f{{animation:fade .8s {EASE} both}}
@keyframes fade{{from{{opacity:0;transform:translateY(8px)}}}}
.hl{{transform-box:fill-box;transform-origin:left;animation:hl 1s {EASE} both}}
@keyframes hl{{from{{transform:scaleX(0)}}}}
.sw{{opacity:0;animation:sw {D}s ease-out infinite}}
@keyframes sw{{0%{{opacity:.14}}6%{{opacity:0}}100%{{opacity:0}}}}'''
    return svg_doc("stack", H, "Stack: Next.js, React, TypeScript, Tailwind CSS, shadcn/ui, Supabase, PostgreSQL, Stripe, Resend, Trigger.dev, Vercel, iOS, Android, WordPress, Figma, Claude Code, Claude API, SEO, AEO, GEO", style, body)


# =====================================================================
# CONTACT
# =====================================================================
def contact(T):
    reset()
    H = 230
    M = 40
    body = frame(T, H)
    body += text("Have a project in mind?", M, 74, 22, T["muted"], "Regular", cls="f")
    url = "launchnest.com.au"
    uw = width(url, 76, "Display-SemiBold", tracking=-0.02)
    body += text(url, M - 2, 160, 76, T["text"], "Display-SemiBold", tracking=-0.02,
                 per_glyph=lambda i, ch: ("g", f"animation-delay:{0.15 + i*0.03:.2f}s"))
    body += f'<rect x="{M}" y="182" width="{uw:.1f}" height="4" fill="{T["accent"]}" class="ul"/>'
    ax = M + uw + 28
    body += f'''<g class="arw"><g transform="translate({ax:.1f} 106)">
  <path d="M6 46 L46 6 M14 6 H46 V38" fill="none" stroke="{T["accent"]}" stroke-width="7" stroke-linecap="square"/></g></g>'''
    style = f'''
.f{{animation:fade .8s {EASE} both}}
@keyframes fade{{from{{opacity:0;transform:translateY(8px)}}}}
.g{{animation:rise 1s {EASE} both}}
@keyframes rise{{from{{opacity:0;transform:translateY(40px)}}}}
.ul{{transform-box:fill-box;transform-origin:left;animation:ul 1.2s {EASE} both .8s}}
@keyframes ul{{from{{transform:scaleX(0)}}}}
.arw{{animation:arw 2.4s {EASE} infinite 1.4s}}
@keyframes arw{{0%,60%,100%{{transform:translate(0,0)}}30%{{transform:translate(8px,-8px)}}}}'''
    body = body.replace(f'<g fill="{T["text"]}"><g class="g"', f'<g fill="{T["text"]}"><g class="g"')
    return svg_doc("contact", H, "Have a project in mind? launchnest.com.au", style, body)


if __name__ == "__main__":
    for theme, T in THEMES.items():
        for fn in (hero, search, architecture, ship, stack, contact):
            save(fn.__name__, theme, fn(T))
