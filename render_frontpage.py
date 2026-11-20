#!/usr/bin/env python3
"""Draw the front page for the make.fun news-image-20261119 entry.

A newspaper front page summing up Thursday 19 November 2026 in one image.
Deterministic: no timestamps, no randomness, no network, fixed fonts and
fixed layout, so the script always writes the same PNG bytes.

Usage: python3 render_frontpage.py [output-path]
Default output: entry.png next to this script.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 36
CW = W - 2 * MARGIN  # content width: 952

BLACK = (17, 17, 17)
RED = (192, 0, 0)
DARK_BLUE = (31, 58, 95)
GREY = (102, 102, 102)
LIGHT_GREY = (242, 242, 242)
WHITE = (255, 255, 255)
GREEN = (0, 128, 0)
ORANGE = (230, 120, 0)
GOLD = (255, 180, 0)
PURPLE = (90, 40, 130)

SERIF_BLACK = "/usr/share/fonts/truetype/noto/NotoSerif-Black.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def wrap(text, fnt, max_width):
    """Greedy word wrap. Returns a list of lines that fit max_width."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if fnt.getlength(trial) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def text_height(fnt):
    ascent, descent = fnt.getmetrics()
    return ascent + descent


def draw_centered(draw, cx, y, text, fnt, fill):
    w = fnt.getlength(text)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return text_height(fnt)


def draw_block(draw, x, y, lines, fnt, fill, leading):
    """Draw wrapped lines left-aligned. Returns the y after the block."""
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def rule(draw, x0, x1, y, weight=2, fill=BLACK):
    draw.rectangle([x0, y, x1, y + weight - 1], fill=fill)


# ---------------------------------------------------------------------------
# Small illustrations, drawn only with PIL shapes.
# Each takes the draw object and a box (x0, y0, x1, y1) to fill.
# ---------------------------------------------------------------------------

def art_scales(draw, x0, y0, x1, y1):
    """Scales of justice."""
    draw.rectangle([x0, y0, x1, y1], fill=LIGHT_GREY)
    cx = (x0 + x1) // 2
    top = y0 + 14
    base = y1 - 14
    mid = (top + base) // 2
    # base and pole
    draw.rectangle([cx - 34, base - 6, cx + 34, base], fill=DARK_BLUE)
    draw.rectangle([cx - 3, top + 16, cx + 3, base - 6], fill=DARK_BLUE)
    # finial
    draw.ellipse([cx - 7, top, cx + 7, top + 14], fill=RED)
    # beam
    draw.rectangle([cx - 78, mid - 3, cx + 78, mid + 3], fill=DARK_BLUE)
    for sign in (-1, 1):
        px = cx + sign * 62
        # hanger lines
        draw.line([px, mid + 3, px - 20, mid + 34], fill=DARK_BLUE, width=2)
        draw.line([px, mid + 3, px + 20, mid + 34], fill=DARK_BLUE, width=2)
        # pan
        draw.pieslice([px - 22, mid + 30, px + 22, mid + 62],
                      0, 180, fill=RED)
        draw.rectangle([px - 22, mid + 30, px + 22, mid + 33], fill=RED)


def art_flags(draw, x0, y0, x1, y1):
    """Three flags: United States, China, Russia."""
    draw.rectangle([x0, y0, x1, y1], fill=LIGHT_GREY)
    w = x1 - x0
    # three poles
    poles = [x0 + w * 0.22, x0 + w * 0.50, x0 + w * 0.78]
    flag_w, flag_h = 52, 32
    top = y0 + 10
    for i, px in enumerate(poles):
        draw.rectangle([px - 2, top, px + 2, y1 - 8], fill=BLACK)
        fx0, fy0 = int(px + 2), top
        fx1, fy1 = fx0 + flag_w, fy0 + flag_h
        if i == 0:  # United States: stripes + blue canton
            for s in range(7):
                col = (178, 34, 52) if s % 2 == 0 else WHITE
                draw.rectangle([fx0, fy0 + s * 5, fx1, fy0 + s * 5 + 5],
                               fill=col)
            draw.rectangle([fx0, fy0, fx0 + 22, fy0 + 16], fill=DARK_BLUE)
            for sx in (6, 14):
                for sy in (5, 11):
                    draw.ellipse([fx0 + sx, fy0 + sy, fx0 + sx + 3,
                                  fy0 + sy + 3], fill=WHITE)
        elif i == 1:  # China: red field, yellow stars
            draw.rectangle([fx0, fy0, fx1, fy1], fill=(222, 41, 16))
            draw.ellipse([fx0 + 6, fy0 + 6, fx0 + 14, fy0 + 14], fill=GOLD)
            for sx, sy in ((26, 5), (34, 11), (34, 19), (26, 24)):
                draw.ellipse([fx0 + sx, fy0 + sy, fx0 + sx + 4,
                              fy0 + sy + 4], fill=GOLD)
        else:  # Russia: white, blue, red horizontal bands
            draw.rectangle([fx0, fy0, fx1, fy0 + 11], fill=WHITE)
            draw.rectangle([fx0, fy0 + 11, fx1, fy0 + 22], fill=(0, 57, 166))
            draw.rectangle([fx0, fy0 + 22, fx1, fy1], fill=(213, 0, 50))
        draw.rectangle([fx0, fy0, fx1, fy1], outline=BLACK, width=1)


def art_chart(draw, x0, y0, x1, y1):
    """A rising stock chart with a +17% label. Fully box-relative."""
    draw.rectangle([x0, y0, x1, y1], fill=LIGHT_GREY)
    h = y1 - y0
    # grid
    for gx in range(x0 + 24, x1 - 8, 34):
        draw.line([gx, y0 + 8, gx, y1 - 6], fill=(220, 220, 220), width=1)
    for gy in range(y0 + 12, y1 - 4, 14):
        draw.line([x0 + 8, gy, x1 - 8, gy], fill=(220, 220, 220), width=1)
    # rising line, from bottom-left to top-right, inside the box
    base = y1 - 8
    top = y0 + 14
    span = base - top
    fracs = [0.0, 0.25, 0.18, 0.55, 0.65, 1.0]
    xs = [x0 + 14, x0 + 52, x0 + 86, x0 + 120, x0 + 154, x0 + 188]
    pts = [(x, base - int(span * f)) for x, f in zip(xs, fracs)]
    draw.line(pts, fill=GREEN, width=4, joint="curve")
    # arrowhead at the last point
    ex, ey = pts[-1]
    draw.polygon([(ex, ey), (ex - 14, ey + 2), (ex - 4, ey + 12)],
                 fill=GREEN)
    fnt = font(SANS_BOLD, 22)
    draw.text((x0 + 12, y0 + 4), "+17%", font=fnt, fill=GREEN)


def art_controller(draw, x0, y0, x1, y1):
    """A game controller with a big VI badge. Scales to the box."""
    draw.rectangle([x0, y0, x1, y1], fill=LIGHT_GREY)
    cx = (x0 + x1) // 2
    cy = (y0 + y1) // 2 + 6
    # body
    draw.rounded_rectangle([cx - 92, cy - 26, cx + 92, cy + 30], radius=22,
                           fill=PURPLE)
    # grips
    draw.ellipse([cx - 96, cy + 2, cx - 58, cy + 44], fill=PURPLE)
    draw.ellipse([cx + 58, cy + 2, cx + 96, cy + 44], fill=PURPLE)
    # d-pad (left)
    draw.rectangle([cx - 66, cy - 14, cx - 54, cy + 10], fill=WHITE)
    draw.rectangle([cx - 72, cy - 8, cx - 48, cy + 4], fill=WHITE)
    # buttons (right): four small coloured dots
    for bx, by, col in ((cx + 56, cy - 14, (255, 220, 0)),
                        (cx + 70, cy - 2, (255, 80, 80)),
                        (cx + 56, cy + 10, (80, 200, 120)),
                        (cx + 42, cy - 2, (90, 160, 255))):
        draw.ellipse([bx - 6, by - 6, bx + 6, by + 6], fill=col)
    # sticks
    draw.ellipse([cx - 26, cy - 4, cx - 10, cy + 12], fill=BLACK)
    draw.ellipse([cx + 10, cy + 2, cx + 26, cy + 18], fill=BLACK)
    # VI badge
    bf = font(SERIF_BLACK, 26)
    draw.text((cx - 9, y0 + 4), "VI", font=bf, fill=RED)


def art_bridge(draw, x0, y0, x1, y1):
    """A suspension bridge over water, smoke over one span.
    Fully box-relative."""
    draw.rectangle([x0, y0, x1, y1], fill=LIGHT_GREY)
    w = x1 - x0
    h = y1 - y0
    sea_top = y1 - max(10, h // 5)
    deck = sea_top - 8
    # sea
    draw.rectangle([x0, sea_top, x1, y1], fill=(90, 140, 190))
    t1 = x0 + w // 4
    t2 = x0 + 3 * w // 4
    top = y0 + 8
    sag = 10
    # towers
    for tx in (t1, t2):
        draw.rectangle([tx - 4, top - 2, tx + 4, deck], fill=DARK_BLUE)
    # main cable: sagging parabola between the tower tops
    pts = []
    for i in range(25):
        t = i / 24.0
        fx = int(t1 + t * (t2 - t1))
        fy = int(top + sag * 4 * t * (1 - t))
        pts.append((fx, fy))
    draw.line(pts, fill=DARK_BLUE, width=2)
    # short anchor cables from towers to the edges
    draw.line([(x0 + 6, top + 10), (t1, top)], fill=DARK_BLUE, width=2)
    draw.line([(t2, top), (x1 - 6, top + 10)], fill=DARK_BLUE, width=2)
    # vertical suspenders
    for i in range(1, 5):
        fx = int(t1 + i * (t2 - t1) / 5)
        t = i / 5.0
        fy = int(top + sag * 4 * t * (1 - t))
        draw.line([(fx, fy), (fx, deck)], fill=DARK_BLUE, width=1)
    # deck
    draw.rectangle([x0 + 6, deck, x1 - 6, deck + 5], fill=BLACK)
    # flame + smoke over the right span
    fx = x0 + int(w * 0.66)
    draw.polygon([(fx - 10, deck), (fx, deck - 18), (fx + 10, deck)],
                 fill=ORANGE)
    for sx, sy, r in ((fx - 6, y0 + 8, 6), (fx + 6, y0 + 4, 8)):
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(130, 130, 130))


def art_parliament(draw, x0, y0, x1, y1):
    """A parliament building: pediment, columns, steps.
    Fully box-relative, so it fits a narrow box too."""
    draw.rectangle([x0, y0, x1, y1], fill=LIGHT_GREY)
    w = x1 - x0
    h = y1 - y0
    cx = (x0 + x1) // 2
    # pediment: small triangle centred above the columns
    ped_h = max(10, h // 4)
    ped_w = min(52, w // 2 - 8)
    draw.polygon([(cx - ped_w, y0 + ped_h + 2), (cx + ped_w, y0 + ped_h + 2),
                  (cx, y0 + 3)], fill=DARK_BLUE)
    draw.ellipse([cx - 4, y0 + ped_h - 3, cx + 4, y0 + ped_h + 5],
                 fill=WHITE)
    # columns: evenly spaced inside the box
    base_y = y1 - 9
    col_top = y0 + ped_h + 4
    n = 5
    col_w = 10
    span = w - 24
    for i in range(n):
        col_x = x0 + 12 + i * (span - col_w) // (n - 1)
        draw.rectangle([col_x, col_top, col_x + col_w, base_y],
                       fill=DARK_BLUE)
    # base and steps
    draw.rectangle([x0 + 8, base_y, x1 - 8, base_y + 4], fill=DARK_BLUE)
    draw.rectangle([x0 + 4, base_y + 5, x1 - 4, y1 - 1], fill=GREY)


ART = {
    "scales": art_scales,
    "flags": art_flags,
    "chart": art_chart,
    "controller": art_controller,
    "bridge": art_bridge,
    "parliament": art_parliament,
}

# ---------------------------------------------------------------------------
# Stories. Wording verified against reporting of 19 November 2026:
# ICJ Myanmar genocide ruling (9-6, first against a state); Shenzhen
# trilateral summit and its four-point peace declaration (no Ukraine, no
# Iran); Anthropic Nasdaq debut (priced $83, opened $111.50, closed +17%
# at $97.17, $81.3bn raised, largest IPO ever; S&P 500 down a fifth
# straight session); GTA VI launches after 13 years; third Ukrainian
# strike on the Kerch Bridge in a week halts rail traffic; Denmark's
# Folketing approves the Greenland defence deal 109-0.
# ---------------------------------------------------------------------------

LEAD = {
    "kicker": "THE HAGUE  •  WORLD COURT",
    "headline": "UN COURT: MYANMAR COMMITTED GENOCIDE",
    "subhead": ("The world court finds Myanmar guilty of genocide against "
                "the Rohingya — the first such ruling against a state, by "
                "9 votes to 6. Refugees in Bangladesh cheered."),
    "art": "scales",
}

BODY = [
    {
        "kicker": "SHENZHEN  •  SUMMIT",
        "headline": "TRUMP, XI AND PUTIN MEET IN SHENZHEN",
        "subhead": ("First-ever trilateral summit ends with a four-point "
                    "peace declaration. It mentions neither Ukraine nor "
                    "Iran."),
        "art": "flags",
    },
    {
        "kicker": "NEW YORK  •  MARKETS",
        "headline": "ANTHROPIC'S RECORD IPO DEBUT",
        "subhead": ("Shares close up 17% after the largest IPO in history "
                    "— $81bn raised. The S&P 500 falls a fifth straight "
                    "session."),
        "art": "chart",
    },
    {
        "kicker": "VICE CITY  •  GAMES",
        "headline": "GTA 6 IS OUT AT LAST",
        "subhead": ("After 13 years, Rockstar's Grand Theft Auto VI "
                    "launches on PlayStation and Xbox. Pre-orders ran far "
                    "ahead of expectations."),
        "art": "controller",
    },
    {
        "kicker": "KERCH  •  WAR",
        "headline": "KYIV HITS CRIMEA BRIDGE AGAIN",
        "subhead": ("A third strike in a week halts rail traffic on the "
                    "Kerch Bridge, hours before Putin meets Trump and Xi."),
        "art": "bridge",
    },
]

CLOSER = {
    "kicker": "COPENHAGEN  •  EUROPE",
    "headline": "DENMARK BACKS GREENLAND DEAL 109–0",
    "subhead": ("Parliament approves the US security deal over Greenland "
                "unanimously, hoping to end the dispute."),
    "art": "parliament",
}

TICKER_LINES = [
    "Haiti police kill 34 gang members in raid  •  Migrant boat capsizes "
    "off Senegal, dozens missing",
    "US Senate rejects Iran war-powers bid 51–48  •  IAEA: North Korea "
    "expands uranium enrichment",
]


def render():
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)

    y = 14
    # ---- Masthead ----
    rule(draw, MARGIN, W - MARGIN, y, 3)
    y += 6
    mast_fnt = font(SERIF_BLACK, 84)
    draw_centered(draw, W // 2, y, "THE WORLD", mast_fnt, BLACK)
    y += text_height(mast_fnt) + 2
    rule(draw, MARGIN, W - MARGIN, y, 2)
    y += 6
    # ---- Dateline: the day must be unmistakable ----
    date_fnt = font(SANS_BOLD, 36)
    draw_centered(draw, W // 2, y, "THURSDAY, 19 NOVEMBER 2026", date_fnt,
                  RED)
    y += text_height(date_fnt) + 6
    rule(draw, MARGIN, W - MARGIN, y, 4)
    y += 10

    # ---- Lead story (full width, art on the right) ----
    lead_top = y
    art_w = 300
    art_x0 = W - MARGIN - art_w
    text_w = art_x0 - 24 - MARGIN
    kicker_fnt = font(SANS_BOLD, 18)
    head_fnt = font(SERIF_BOLD, 44)
    sub_fnt = font(SANS, 21)
    draw.text((MARGIN, lead_top), LEAD["kicker"], font=kicker_fnt, fill=RED)
    hy = lead_top + 24
    head_lines = wrap(LEAD["headline"], head_fnt, text_w)
    hy = draw_block(draw, MARGIN, hy, head_lines, head_fnt, BLACK, 48)
    sub_lines = wrap(LEAD["subhead"], sub_fnt, text_w)
    sy = hy + 6
    sy = draw_block(draw, MARGIN, sy, sub_lines, sub_fnt, BLACK, 25)
    content_h = sy - lead_top
    art_h = max(content_h, 150)
    ART[LEAD["art"]](draw, art_x0, lead_top, W - MARGIN, lead_top + art_h)
    y = lead_top + max(art_h, content_h) + 10
    rule(draw, MARGIN, W - MARGIN, y, 2)
    y += 6

    # ---- Body stories: two columns, two rows.
    # Each cell's height is measured from its own wrapped text, so no
    # divider ever crosses a line of text.
    col_w = (CW - 24) // 2
    for row in range(2):
        row_top = y
        row_bottom = row_top
        for col in range(2):
            story = BODY[row * 2 + col]
            x0 = MARGIN + col * (col_w + 24)
            cy = row_top
            ART[story["art"]](draw, x0, cy, x0 + col_w, cy + 40)
            cy += 40 + 5
            kf = font(SANS_BOLD, 16)
            draw.text((x0, cy), story["kicker"], font=kf, fill=RED)
            cy += 20
            hf = font(SERIF_BOLD, 31)
            lines = wrap(story["headline"], hf, col_w)
            cy = draw_block(draw, x0, cy, lines, hf, BLACK, 36)
            cy += 3
            sf = font(SANS, 18)
            slines = wrap(story["subhead"], sf, col_w)
            cy = draw_block(draw, x0, cy, slines, sf, BLACK, 21)
            row_bottom = max(row_bottom, cy)
        y = row_bottom + 10
        rule(draw, MARGIN, W - MARGIN, y, 2)
        y += 6

    # ---- Closer story (full width, art on the left) ----
    closer_top = y
    art_w2 = 130
    ART[CLOSER["art"]](draw, MARGIN, closer_top, MARGIN + art_w2,
                       closer_top + 100)
    tx = MARGIN + art_w2 + 20
    tw = W - MARGIN - tx
    kf = font(SANS_BOLD, 16)
    draw.text((tx, closer_top), CLOSER["kicker"], font=kf, fill=RED)
    cy = closer_top + 20
    hf = font(SERIF_BOLD, 36)
    lines = wrap(CLOSER["headline"], hf, tw)
    cy = draw_block(draw, tx, cy, lines, hf, BLACK, 42)
    cy += 2
    sf = font(SANS, 19)
    slines = wrap(CLOSER["subhead"], sf, tw)
    cy = draw_block(draw, tx, cy, slines, sf, BLACK, 23)
    y = max(closer_top + 100, cy) + 10
    rule(draw, MARGIN, W - MARGIN, y, 2)
    y += 6

    # ---- Bottom ticker ----
    ticker_h = 42
    assert y + ticker_h <= H - 8, "layout overflow: ticker ends at %d" % (
        y + ticker_h)
    draw.rectangle([MARGIN, y, W - MARGIN, y + ticker_h], fill=RED)
    tf = font(SANS_BOLD, 17)
    ty = y + 3
    for line in TICKER_LINES:
        twd = tf.getlength(line)
        draw.text((W // 2 - twd / 2, ty), line, font=tf, fill=WHITE)
        ty += 19

    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img = render()
    img.save(out, format="PNG")
    print("wrote", out, img.size, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
