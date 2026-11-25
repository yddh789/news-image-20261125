#!/usr/bin/env python3
"""news-image-20261125: draw one image summing up Wednesday 25 November 2026.

Reads nothing but its own constants, needs no network, and writes the same
bytes on every run: Pillow draws fixed shapes and text at fixed positions.
Output goes to /output/entry.png when that directory exists (the grader's
sandbox), else to output/25-nov-2026-news.png next to this file.
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# Palette: deep ink background, paper-white cards, one accent per story.
INK = (13, 22, 38)
PAPER = (247, 245, 239)
CARD = (255, 255, 255)
MUTED = (96, 104, 122)
DARK = (20, 28, 46)
GOLD = (214, 158, 46)
RED = (178, 44, 36)
TEAL = (14, 116, 110)
BLUE = (29, 78, 150)
GREEN = (34, 120, 66)
PURPLE = (104, 66, 150)

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_text(draw, text, fnt, max_w, max_lines):
    """Wrap text; if it overflows max_lines, shrink the font until it fits."""
    size = fnt.size
    while size > 12:
        lines = wrap(draw, text, font(size), max_w)
        if len(lines) <= max_lines:
            return lines, font(size)
        size -= 1
    return wrap(draw, text, font(size), max_w), font(size)


# Each story: (tag, tag colour, headline, body, glyph name)
STORIES = [
    (
        "MIDDLE EAST",
        RED,
        "Two tankers hit mines in Hormuz",
        "Iran's Revolutionary Guard says two oil tankers struck naval mines "
        "and caught fire in the Strait of Hormuz, claiming they took an "
        "unauthorised route.",
        "ship",
    ),
    (
        "YEMEN / SAUDI ARABIA",
        (176, 92, 20),
        "Houthis claim refinery strike",
        "Yemen's Houthis say they attacked Saudi Arabia's Ras Tanura oil "
        "refinery, a day after a Houthi drone hit a tower in Riyadh and "
        "injured 11 people.",
        "flame",
    ),
    (
        "UKRAINE WAR",
        BLUE,
        "Kyiv's drones hit refineries, sink warship",
        "Ukrainian drones hit two Rosneft refineries in Russia's Samara "
        "region. Zelenskyy confirms sea drones sank a Russian corvette off "
        "Benghazi, Libya.",
        "drone",
    ),
    (
        "MARKETS",
        TEAL,
        "Asian stocks tumble",
        "South Korea's KOSPI plunges 6.2% and Japan's Nikkei falls 2.8% as "
        "AI shares slide: Samsung -9.9%, SK Hynix -11.1%, SoftBank -14.8%.",
        "chart",
    ),
    (
        "SPACE",
        PURPLE,
        "Pakistan's first astronaut reaches Tiangong",
        "China's Shenzhou-24 docks with the Tiangong space station about "
        "three and a half hours after launch, carrying Pakistan's first "
        "astronaut.",
        "rocket",
    ),
    (
        "PACIFIC",
        GREEN,
        "Australia-Solomons treaty signed",
        "Australia and Solomon Islands sign a treaty in Canberra barring "
        "any foreign military or security base from being built on the "
        "islands.",
        "globe",
    ),
]


def glyph(draw, kind, cx, cy, colour):
    """Small geometric pictogram, drawn with Pillow primitives only."""
    if kind == "ship":
        draw.polygon([(cx - 26, cy + 8), (cx + 26, cy + 8),
                      (cx + 16, cy + 22), (cx - 16, cy + 22)], fill=colour)
        draw.line([cx, cy - 26, cx, cy + 8], fill=colour, width=4)
        draw.polygon([(cx, cy - 26), (cx, cy + 2), (cx + 18, cy + 2)], fill=colour)
        draw.line([(cx - 26, cy + 30), (cx + 26, cy + 30)], fill=colour, width=4)
    elif kind == "flame":
        draw.polygon([(cx, cy - 26), (cx + 8, cy - 8), (cx + 18, cy + 8),
                      (cx + 14, cy + 22), (cx - 14, cy + 22), (cx - 18, cy + 8),
                      (cx - 8, cy - 8)], fill=colour)
        draw.polygon([(cx, cy - 6), (cx + 7, cy + 6), (cx + 5, cy + 16),
                      (cx - 5, cy + 16), (cx - 7, cy + 6)], fill=(244, 196, 66))
    elif kind == "drone":
        draw.ellipse([cx - 12, cy - 8, cx + 12, cy + 8], fill=colour)
        for dx in (-24, 24):
            draw.ellipse([cx + dx - 9, cy - 22, cx + dx + 9, cy - 4], outline=colour, width=4)
            draw.line([cx + dx, cy - 6, cx + (dx // 3), cy - 4], fill=colour, width=3)
        draw.line([cx - 8, cy + 16, cx + 8, cy + 16], fill=colour, width=4)
    elif kind == "chart":
        draw.line([(cx - 26, cy + 18), (cx - 26, cy - 22)], fill=colour, width=4)
        draw.line([(cx - 26, cy + 18), (cx + 26, cy + 18)], fill=colour, width=4)
        draw.line([(cx - 22, cy + 10), (cx - 8, cy - 2), (cx + 4, cy + 6),
                   (cx + 22, cy - 16)], fill=colour, width=5)
        draw.polygon([(cx + 22, cy - 16), (cx + 12, cy - 16), (cx + 22, cy - 6)], fill=colour)
    elif kind == "rocket":
        draw.polygon([(cx, cy - 28), (cx + 12, cy - 2), (cx + 12, cy + 12),
                      (cx - 12, cy + 12), (cx - 12, cy - 2)], fill=colour)
        draw.ellipse([cx - 5, cy - 12, cx + 5, cy - 2], fill=PAPER)
        draw.polygon([(cx - 12, cy + 8), (cx - 22, cy + 22), (cx - 12, cy + 16)], fill=colour)
        draw.polygon([(cx + 12, cy + 8), (cx + 22, cy + 22), (cx + 12, cy + 16)], fill=colour)
        draw.polygon([(cx - 5, cy + 14), (cx + 5, cy + 14), (cx, cy + 28)], fill=GOLD)
    elif kind == "globe":
        draw.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], outline=colour, width=4)
        draw.ellipse([cx - 10, cy - 24, cx + 10, cy + 24], outline=colour, width=3)
        draw.line([cx - 24, cy, cx + 24, cy], fill=colour, width=3)
        draw.arc([cx - 24, cy - 10, cx + 24, cy + 10], start=0, end=360, fill=colour, width=3)


def draw_card(draw, x, y, w, h, story):
    tag, colour, headline, body, kind = story
    draw.rounded_rectangle([x, y, x + w, y + h], radius=18, fill=CARD)
    draw.rounded_rectangle([x, y, x + w, y + 8], radius=4, fill=colour)
    # pictogram in a tinted disc, top right
    cx, cy = x + w - 52, y + 52
    draw.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], fill=(238, 240, 244))
    glyph(draw, kind, cx, cy, colour)
    # tag
    tf = font(17, bold=True)
    draw.text((x + 22, y + 24), tag, font=tf, fill=colour)
    # headline, auto-fit to at most 2 lines
    head_lines, hf = fit_text(draw, headline, font(30, bold=True), w - 118, 2)
    hy = y + 56
    for line in head_lines:
        draw.text((x + 22, hy), line, font=hf, fill=DARK)
        hy += hf.size + 4
    # body, at most 4 lines
    body_lines, bf = fit_text(draw, body, font(21), w - 44, 4)
    by = hy + 10
    for line in body_lines:
        draw.text((x + 22, by), line, font=bf, fill=MUTED)
        by += bf.size + 7


def main():
    img = Image.new("RGB", (W, H), INK)
    draw = ImageDraw.Draw(img)

    # Masthead
    draw.text((40, 30), "THE WORLD IN ONE DAY", font=font(46, bold=True), fill=PAPER)
    draw.text((40, 92), "Wednesday, 25 November 2026", font=font(28), fill=GOLD)
    draw.line([(40, 138), (984, 138)], fill=GOLD, width=3)
    draw.text((40, 150), "Six stories that defined the day, from Hormuz to Tiangong.",
              font=font(22), fill=(180, 188, 204))

    # 2 x 3 grid of story cards
    gx, gy = 40, 196
    cw, ch = 462, 240
    gap_x, gap_y = 20, 20
    for i, story in enumerate(STORIES):
        col, row = i % 2, i // 2
        draw_card(draw, gx + col * (cw + gap_x), gy + row * (ch + gap_y),
                  cw, ch, story)

    # Footer
    draw.text((40, 984), "Sources: Just Security Early Edition, AP, Reuters, BBC, "
              "China Manned Space Agency  |  25 Nov 2026",
              font=font(16), fill=(150, 158, 174))

    outdir = "/output" if os.path.isdir("/output") else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(outdir, exist_ok=True)
    name = "entry.png" if outdir == "/output" else "25-nov-2026-news.png"
    path = os.path.join(outdir, name)
    img.save(path, "PNG")
    print(f"wrote {path} ({os.path.getsize(path)} bytes)")


if __name__ == "__main__":
    main()
