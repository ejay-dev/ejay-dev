"""Outline text renderer: turns strings into SVG <use> references to glyph
paths (with GPOS pair kerning), so the README renders identically everywhere."""
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

FONT_DIR = "/usr/share/fonts/opentype/inter/"
MONO_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


class Font:
    def __init__(self, key, path):
        self.key = key
        self.tt = TTFont(path)
        self.upm = self.tt["head"].unitsPerEm
        self.cmap = self.tt.getBestCmap()
        self.gs = self.tt.getGlyphSet()
        self.hmtx = self.tt["hmtx"].metrics
        self.order = {g: i for i, g in enumerate(self.tt.getGlyphOrder())}
        self.kern = self._load_kern()
        self.used = {}

    # ---- kerning from GPOS PairPos (format 1 & 2, incl. extension lookups)
    def _load_kern(self):
        pairs, classes = {}, []
        if "GPOS" not in self.tt:
            return (pairs, classes)
        gpos = self.tt["GPOS"].table
        idx = set()
        for fr in gpos.FeatureList.FeatureRecord:
            if fr.FeatureTag == "kern":
                idx.update(fr.Feature.LookupListIndex)
        for li in sorted(idx):
            lk = gpos.LookupList.Lookup[li]
            for st in lk.SubTable:
                if lk.LookupType == 9:
                    st = st.ExtSubTable
                if getattr(st, "LookupType", 2) != 2 and lk.LookupType != 9:
                    continue
                if not hasattr(st, "Format"):
                    continue
                cov = st.Coverage.glyphs
                if st.Format == 1:
                    for g1, ps in zip(cov, st.PairSet):
                        for pvr in ps.PairValueRecord:
                            v = getattr(pvr.Value1, "XAdvance", 0) if pvr.Value1 else 0
                            if v and (g1, pvr.SecondGlyph) not in pairs:
                                pairs[(g1, pvr.SecondGlyph)] = v
                elif st.Format == 2:
                    classes.append((set(cov), st.ClassDef1.classDefs, st.ClassDef2.classDefs, st.Class1Record))
        return (pairs, classes)

    def kerning(self, a, b):
        pairs, classes = self.kern
        if (a, b) in pairs:
            return pairs[(a, b)]
        for cov, c1, c2, recs in classes:
            if a in cov:
                r = recs[c1.get(a, 0)].Class2Record[c2.get(b, 0)]
                v = getattr(r.Value1, "XAdvance", 0) if r.Value1 else 0
                return v or 0
        return 0

    def gname(self, ch):
        return self.cmap.get(ord(ch)) or self.cmap.get(ord("?"))

    def glyph_id(self, g):
        gid = f"{self.key}{self.order[g]}"
        if gid not in self.used:
            pen = SVGPathPen(self.gs)
            self.gs[g].draw(pen)
            self.used[gid] = pen.getCommands()
        return gid

    def layout(self, text, size, tracking=0.0):
        """Returns list of (char, glyph, x_in_px) and total width in px."""
        s = size / self.upm
        x, out, prev = 0.0, [], None
        for ch in text:
            g = self.gname(ch)
            if prev is not None:
                x += self.kerning(prev, g)
            out.append((ch, g, x * s))
            x += self.hmtx[g][0] + tracking * self.upm
            prev = g
        return out, (x - tracking * self.upm) * s

    def width(self, text, size, tracking=0.0):
        return self.layout(text, size, tracking)[1]

    def defs(self):
        return "".join(f'<path id="{k}" d="{d}"/>' for k, d in self.used.items() if d)


FONTS = {}
def font(name):
    if name not in FONTS:
        if name == "mono":
            FONTS[name] = Font("m", MONO_PATH)
        else:
            key = {"Display-Bold": "db", "Display-SemiBold": "ds", "Display-Medium": "dm",
                   "Regular": "r", "Medium": "md", "SemiBold": "sb", "Bold": "b"}[name]
            path = FONT_DIR + (f"InterDisplay-{name.split('-')[1]}.otf" if name.startswith("Display") else f"Inter-{name}.otf")
            FONTS[name] = Font(key, path)
    return FONTS[name]


def text(s, x, y, size, fill, face="Regular", anchor="start", tracking=0.0,
         per_glyph=None, cls=None, style=None):
    """Render a string as outlined glyphs.
    per_glyph: optional callable(i, ch) -> (class, style) to wrap each glyph for staggered animation."""
    f = font(face)
    glyphs, w = f.layout(s, size, tracking)
    if anchor == "middle":
        x -= w / 2
    elif anchor == "end":
        x -= w
    sc = size / f.upm
    attrs = (f' class="{cls}"' if cls else "") + (f' style="{style}"' if style else "")
    if per_glyph is None:
        uses = "".join(
            f'<use href="#{f.glyph_id(g)}" x="{gx / sc:.0f}"/>' for ch, g, gx in glyphs if ch != " "
        )
        return f'<g fill="{fill}"{attrs}><g transform="translate({x:.2f} {y:.2f}) scale({sc:.5f} {-sc:.5f})">{uses}</g></g>'
    parts = []
    for i, (ch, g, gx) in enumerate(glyphs):
        if ch == " ":
            continue
        c, st = per_glyph(i, ch)
        parts.append(
            f'<g class="{c}" style="{st}"><g transform="translate({x + gx:.2f} {y:.2f}) scale({sc:.5f} {-sc:.5f})">'
            f'<use href="#{f.glyph_id(g)}"/></g></g>'
        )
    return f'<g fill="{fill}"{attrs}>{"".join(parts)}</g>'


def width(s, size, face="Regular", tracking=0.0):
    return font(face).width(s, size, tracking)


def wrap(s, size, maxw, face="Regular"):
    lines, cur = [], ""
    for word in s.split():
        t = (cur + " " + word).strip()
        if width(t, size, face) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


def glyph_x_positions(s, size, face="Regular"):
    glyphs, w = font(face).layout(s, size)
    f = font(face)
    out = []
    for ch, g, gx in glyphs:
        out.append(gx + f.hmtx[g][0] * size / f.upm)
    return out, w


def all_defs():
    d = "".join(f.defs() for f in FONTS.values())
    return f"<defs>{d}</defs>"


def reset():
    for f in FONTS.values():
        f.used = {}
