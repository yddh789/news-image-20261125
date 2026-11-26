#!/usr/bin/env python3
"""news-image-20261125: draw one image summing up Wednesday 25 November 2026.

Standard library only. The grader's sandbox has no image libraries and no system
fonts, so this program draws everything itself:

* a pixel canvas (bytearray, RGB) with its own rect/line/circle/polygon
  primitives,
* an embedded 5x7 bitmap font (A-Z, a-z, 0-9 and common punctuation),
  rendered by plotting scaled dots -- no font files needed,
* a hand-written PNG encoder (signature, IHDR, zlib-compressed IDAT
  scanlines with filter byte 0, IEND).

Reads nothing but its own constants, needs no network, no clock and no
randomness, and writes the same bytes on every run. Output goes to
$MAKEFUN_OUTPUT_DIR/entry.png when set, else /output/entry.png when that
directory exists (the grader's sandbox), else output/25-nov-2026-news.png
next to this file.
"""

import math
import os
import struct
import zlib

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
DISC = (238, 240, 244)
SUBTLE = (180, 188, 204)
FAINT = (150, 158, 174)

# ---------------------------------------------------------------- font
# 5x7 bitmap font. Each glyph is 7 rows of 5 characters ('#' = on).
FONT = {
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "a": (".....", ".....", ".####", "....#", ".####", "#...#", ".####"),
    "b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    "c": (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    "d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    "e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    "f": ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
    "g": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    "h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "i": ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    "j": ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", "#..#."),
    "k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    "l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    "n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    "p": (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    "q": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    "r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    "s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    "t": (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    "u": (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    "v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "w": (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    "y": (".....", ".....", "#...#", "#...#", "#...#", ".####", "....#"),
    "z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": (".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ".": (".....", ".....", ".....", ".....", ".....", ".....", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "=": (".....", ".....", ".###.", ".....", ".###.", ".....", "....."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "|": ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "*": (".....", ".#.#.", "..#..", ".###.", "..#..", ".#.#.", "....."),
    "@": (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "<": ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    ">": (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    "[": (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    "]": (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
    "~": (".....", ".....", ".##..", "#..##", ".....", ".....", "....."),
    "^": ("..#..", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "`": ("..#..", ".#...", ".....", ".....", ".....", ".....", "....."),
    "\\": ("#....", "#....", ".#...", ".#...", "..#..", "..#..", "...#."),
}


def text_width(text, scale):
    """Width in pixels of text drawn at the given scale."""
    return len(text) * 6 * scale


def wrap(text, scale, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if text_width(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    """An RGB pixel canvas backed by a bytearray."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bytes(bg)) * (w * h)

    def set(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(colour)

    def fill_rect(self, x0, y0, x1, y1, colour):
        x0 = max(x0, 0)
        y0 = max(y0, 0)
        x1 = min(x1, self.w)
        y1 = min(y1, self.h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(colour) * (x1 - x0)
        for y in range(y0, y1):
            i = (y * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def hline(self, x0, x1, y, colour, width=1):
        self.fill_rect(x0, y - width // 2, x1, y - width // 2 + width, colour)

    def vline(self, x, y0, y1, colour, width=1):
        self.fill_rect(x - width // 2, y0, x - width // 2 + width, y1, colour)

    def line(self, x0, y0, x1, y1, colour, width=1):
        """Bresenham line; width is drawn as a small filled square."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        r = width // 2
        while True:
            self.fill_rect(x0 - r, y0 - r, x0 - r + width, y0 - r + width,
                           colour)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, colour):
        """Filled circle."""
        for dy in range(-r, r + 1):
            dx = math.isqrt(max(r * r - dy * dy, 0))
            self.fill_rect(cx - dx, cy + dy, cx + dx + 1, cy + dy + 1, colour)

    def ring(self, cx, cy, r, colour, width=3):
        """Circle outline, width pixels thick."""
        half = width / 2.0
        for y in range(cy - r - width, cy + r + width + 1):
            for x in range(cx - r - width, cx + r + width + 1):
                d = math.hypot(x - cx, y - cy)
                if abs(d - r) <= half:
                    self.set(x, y, colour)

    def ellipse(self, cx, cy, rx, ry, colour):
        """Filled ellipse."""
        for dy in range(-ry, ry + 1):
            span = rx * math.sqrt(max(1.0 - (dy * dy) / (ry * ry), 0.0))
            dx = int(span)
            self.fill_rect(cx - dx, cy + dy, cx + dx + 1, cy + dy + 1, colour)

    def ellipse_ring(self, cx, cy, rx, ry, colour, width=3):
        """Ellipse outline, width pixels thick."""
        half = width / 2.0
        for y in range(cy - ry - width, cy + ry + width + 1):
            for x in range(cx - rx - width, cx + rx + width + 1):
                v = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
                if abs(math.sqrt(max(v, 0.0)) - 1.0) * min(rx, ry) <= half:
                    self.set(x, y, colour)

    def polygon(self, points, colour):
        """Filled polygon, scanline fill."""
        if not points:
            return
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.fill_rect(int(xs[i]), y, int(xs[i + 1]) + 1, y + 1,
                               colour)

    def round_rect(self, x, y, w, h, r, colour):
        """Filled rectangle with rounded corners of radius r."""
        self.fill_rect(x + r, y, x + w - r, y + h, colour)
        self.fill_rect(x, y + r, x + w, y + h - r, colour)
        for cx, cy in ((x + r, y + r), (x + w - r - 1, y + r),
                       (x + r, y + h - r - 1), (x + w - r - 1, y + h - r - 1)):
            self.disc(cx, cy, r, colour)

    # ------------------------------------------------------------ text
    def glyph(self, ch, x, y, scale, colour):
        rows = FONT.get(ch)
        if rows is None:
            return
        for ry, row in enumerate(rows):
            for rx, cell in enumerate(row):
                if cell == "#":
                    self.fill_rect(x + rx * scale, y + ry * scale,
                                   x + (rx + 1) * scale, y + (ry + 1) * scale,
                                   colour)

    def text(self, x, y, s, scale, colour):
        for ch in s:
            self.glyph(ch, x, y, scale, colour)
            x += 6 * scale


# ---------------------------------------------------------------- PNG
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def save_png(canvas, path):
    """Encode the canvas as a 1024x1024 RGB PNG (filter byte 0 per row)."""
    raw = bytearray()
    w = canvas.w
    for y in range(canvas.h):
        raw.append(0)
        i = y * w * 3
        raw += canvas.px[i:i + w * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2,
                                       0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------- stories
# Each story: (tag, tag colour, headline, body, pictogram name)
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


def pictogram(cv, kind, cx, cy, colour):
    """Small geometric pictogram, drawn with canvas primitives only."""
    if kind == "ship":
        cv.polygon([(cx - 26, cy + 8), (cx + 26, cy + 8),
                    (cx + 16, cy + 22), (cx - 16, cy + 22)], colour)
        cv.vline(cx, cy - 26, cy + 8, colour, width=4)
        cv.polygon([(cx, cy - 26), (cx, cy + 2), (cx + 18, cy + 2)], colour)
        cv.hline(cx - 26, cx + 26, cy + 30, colour, width=4)
    elif kind == "flame":
        cv.polygon([(cx, cy - 26), (cx + 8, cy - 8), (cx + 18, cy + 8),
                    (cx + 14, cy + 22), (cx - 14, cy + 22), (cx - 18, cy + 8),
                    (cx - 8, cy - 8)], colour)
        cv.polygon([(cx, cy - 6), (cx + 7, cy + 6), (cx + 5, cy + 16),
                    (cx - 5, cy + 16), (cx - 7, cy + 6)], (244, 196, 66))
    elif kind == "drone":
        cv.ellipse(cx, cy, 12, 8, colour)
        for dx in (-24, 24):
            cv.ellipse_ring(cx + dx, cy - 13, 9, 9, colour, width=3)
            cv.line(cx + dx, cy - 6, cx + dx // 3, cy - 4, colour, width=3)
        cv.hline(cx - 8, cx + 8, cy + 16, colour, width=4)
    elif kind == "chart":
        cv.vline(cx - 26, cy - 22, cy + 18, colour, width=4)
        cv.hline(cx - 26, cx + 26, cy + 18, colour, width=4)
        cv.line(cx - 22, cy + 10, cx - 8, cy - 2, colour, width=5)
        cv.line(cx - 8, cy - 2, cx + 4, cy + 6, colour, width=5)
        cv.line(cx + 4, cy + 6, cx + 22, cy - 16, colour, width=5)
        cv.polygon([(cx + 22, cy - 16), (cx + 12, cy - 16),
                    (cx + 22, cy - 6)], colour)
    elif kind == "rocket":
        cv.polygon([(cx, cy - 28), (cx + 12, cy - 2), (cx + 12, cy + 12),
                    (cx - 12, cy + 12), (cx - 12, cy - 2)], colour)
        cv.disc(cx, cy - 7, 5, PAPER)
        cv.polygon([(cx - 12, cy + 8), (cx - 22, cy + 22), (cx - 12, cy + 16)],
                   colour)
        cv.polygon([(cx + 12, cy + 8), (cx + 22, cy + 22), (cx + 12, cy + 16)],
                   colour)
        cv.polygon([(cx - 5, cy + 14), (cx + 5, cy + 14), (cx, cy + 28)],
                   GOLD)
    elif kind == "globe":
        cv.ring(cx, cy, 24, colour, width=4)
        cv.ellipse_ring(cx, cy, 10, 24, colour, width=3)
        cv.hline(cx - 24, cx + 24, cy, colour, width=3)


def draw_card(cv, x, y, w, h, story):
    tag, colour, headline, body, kind = story
    cv.round_rect(x, y, w, h, 18, CARD)
    cv.fill_rect(x + 4, y, x + w - 4, y + 8, colour)
    # pictogram in a tinted disc, top right
    cx, cy = x + w - 52, y + 52
    cv.disc(cx, cy, 34, DISC)
    pictogram(cv, kind, cx, cy, colour)
    # tag
    cv.text(x + 22, y + 24, tag, 2, colour)
    # headline, at most 3 lines at scale 3
    head_lines = wrap(headline, 3, w - 118)[:3]
    hy = y + 52
    for line in head_lines:
        cv.text(x + 22, hy, line, 3, DARK)
        hy += 25
    # body, at most 5 lines at scale 2
    body_lines = wrap(body, 2, w - 44)[:5]
    by = hy + 8
    for line in body_lines:
        cv.text(x + 22, by, line, 2, MUTED)
        by += 18


def main():
    cv = Canvas(W, H, INK)

    # Masthead
    cv.text(40, 34, "THE WORLD IN ONE DAY", 6, PAPER)
    cv.text(40, 92, "Wednesday, 25 November 2026", 4, GOLD)
    cv.hline(40, 984, 140, GOLD, width=3)
    cv.text(40, 154, "Six stories that defined the day, from Hormuz to Tiangong.",
            2, SUBTLE)

    # 2 x 3 grid of story cards
    gx, gy = 40, 196
    cw, ch = 462, 240
    gap_x, gap_y = 20, 20
    for i, story in enumerate(STORIES):
        col, row = i % 2, i // 2
        draw_card(cv, gx + col * (cw + gap_x), gy + row * (ch + gap_y),
                  cw, ch, story)

    # Footer
    cv.text(40, 972, "Sources: Just Security Early Edition, AP, Reuters, BBC,", 2,
            FAINT)
    cv.text(40, 992, "China Manned Space Agency  |  25 Nov 2026", 2, FAINT)

    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if outdir:
        name = "entry.png"
    elif os.path.isdir("/output"):
        outdir = "/output"
        name = "entry.png"
    else:
        outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "output")
        name = "25-nov-2026-news.png"
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, name)
    size = save_png(cv, path)
    print(f"wrote {path} ({size} bytes)")


if __name__ == "__main__":
    main()
