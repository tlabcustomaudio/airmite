"""AirMite wiring pictures + schematics -> docs/*.png
Run: python tools/drawings.py   (needs matplotlib)"""
import os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs")
RED, BLK, BLU, ORA, GRN = "#d62728", "#222222", "#1f77b4", "#c8891a", "#2ca02c"
LIGHT = {RED: "#ff8080", BLK: "#ffffff", BLU: "#6cb6ff", ORA: "#f0b23a", GRN: "#7fdc7f"}
BOARD_C, SHT_C, PAD_C = "#2b2f36", "#5b2d8e", "#d8c26a"


def canvas(w, h, title, sub):
    fig, ax = plt.subplots(figsize=(w / 11, h / 11))
    ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis("off"); ax.set_aspect("equal")
    ax.text(4, h - 5, title, fontsize=16, weight="bold")
    ax.text(4, h - 9.5, sub, fontsize=9, color="#666")
    return fig, ax


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=150, facecolor="white", bbox_inches="tight")
    plt.close(fig); print("wrote", name)


def board(ax, x, y, w, h, c, title, sub=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.2",
                                fc=c, ec="#111", lw=1.2, zorder=4))
    ax.text(x + w / 2, y + h + (8 if sub else 4), title, ha="center", fontsize=11.5, weight="bold")
    if sub:
        ax.text(x + w / 2, y + h + 4, sub, ha="center", fontsize=8, color="#666")


def pad(ax, x, y, r=0.95):
    ax.add_patch(Circle((x, y), r, fc=PAD_C, ec="#111", lw=0.8, zorder=6))


def route(ax, pts, color, lw=2.6, z=3):
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=color, lw=lw, zorder=z,
            solid_capstyle="round", solid_joinstyle="round")


def note(ax, x, y, title, body):
    ax.text(x, y, title, fontsize=10.5, weight="bold", va="top")
    ax.text(x, y - 3.8, body, fontsize=9, va="top", linespacing=1.7, color="#222")


def dev_board(ax, x, y, w, h, title, sub, left, right, usb_label):
    """board seen from the component side, USB-C at the top; pins top to bottom.
    left/right: lists of (label, colour or None). Returns {label: (x, y)} of each pad."""
    board(ax, x, y, w, h, BOARD_C, title, sub)
    ax.add_patch(Rectangle((x + w / 2 - 4, y + h - 0.6), 8, 2.4, fc="#9aa0a6", ec="#111", lw=0.8, zorder=5))
    ax.text(x + w / 2, y + h - 4, usb_label, ha="center", fontsize=7, color="#9aa3ad", zorder=5)
    pos, step = {}, (h - 10) / (max(len(left), len(right)) - 1)
    for side, pins in ((0, left), (1, right)):
        for i, (t, c) in enumerate(pins):
            py = y + h - 7 - step * i
            px = x + (w - 1.9 if side else 1.9)
            pad(ax, px, py)
            ax.text(px + (-1.7 if side else 1.7), py, t, ha="right" if side else "left", va="center",
                    fontsize=8, zorder=5, color=LIGHT.get(c, "#9aa3ad"), weight="bold" if c else "normal")
            pos[t] = (px, py)
    return pos


def sht41(ax, x, y):
    board(ax, x, y, 22, 24, SHT_C, "SHT40 / SHT41 breakout")
    ax.add_patch(Circle((x + 4.5, y + 19), 2.6, fc="#efeff0", ec="#111", lw=0.8, zorder=5))
    ax.text(x + 13.5, y + 14, "pull-ups\non board", ha="center", va="center", fontsize=8,
            color="#d8d2e6", zorder=5)
    pos = {}
    for i, (t, c) in enumerate([("VIN", RED), ("GND", BLK), ("SCL", ORA), ("SDA", BLU)]):
        px = x + 3.4 + i * 5.1
        pad(ax, px, y + 2.6)
        ax.text(px, y + 6.4, t, ha="center", fontsize=8.5, weight="bold", zorder=5, color=LIGHT[c])
        pos[t] = (px, y + 2.6)
    return pos


def i2c_wires(ax, b, s, lanes, x_out_r, x_out_l, pins):
    """four wires board -> SHT; pins = board labels for 3V3, GND, SDA, SCL"""
    v, g, sda, scl = pins
    for (bp, sp, col, lane, xo) in ((v, "VIN", RED, lanes[0], x_out_r[0]), (g, "GND", BLK, lanes[1], x_out_r[1]),
                                    (scl, "SCL", ORA, lanes[2], x_out_l[0]), (sda, "SDA", BLU, lanes[3], x_out_l[1])):
        bx, by = b[bp]; sx, sy = s[sp]
        route(ax, [(bx, by), (xo, by), (xo, lane), (sx, lane), (sx, sy)], col)


# ----------------------------------------------------------------------- wiring: USB versions
def wiring_usb():
    fig, ax = canvas(165, 100, "AirMite USB — ESP32-C3 SuperMini (or Plus) + SHT41",
                     "firmware airmite-usb / airmite-usb-plus   ·   i2c:  SDA = GPIO5   SCL = GPIO6")
    left = [("GPIO5", BLU), ("GPIO6", ORA), ("GPIO7", None), ("GPIO8", None), ("GPIO9", None),
            ("GPIO10", None), ("GPIO20", None), ("GPIO21", None)]
    right = [("5V", None), ("GND", BLK), ("3V3", RED), ("GPIO4", None), ("GPIO3", None),
             ("GPIO2", None), ("GPIO1", None), ("GPIO0", None)]
    b = dev_board(ax, 60, 42, 26, 34, "ESP32-C3 SuperMini", "component side, USB-C up", left, right, "")
    s = sht41(ax, 118, 48)
    i2c_wires(ax, b, s, (37, 34, 31, 28), (91, 94), (56, 53), ("3V3", "GND", "GPIO5", "GPIO6"))
    note(ax, 4, 86, "Four wires", "3V3     →  VIN   (never 5V)\nGND    →  GND\nGPIO5  →  SDA\nGPIO6  →  SCL")
    note(ax, 4, 60, "Good to know",
         "Pin names are printed on the board:\nfollow them, not the picture, if your\nclone is laid out differently.\n\n"
         "Keep the SHT41 away from the board\n(a short cable, other side of a wall\nin the case): the ESP32 warms it.")
    note(ax, 60, 20, "Plus version",
         "Same wiring. The Plus has an RGB LED on GPIO8: the airmite-usb-plus firmware switches it off.\n"
         "Do not use GPIO8 / GPIO9 for the sensor (LED and boot pin).")
    save(fig, "wiring-usb.png")


# ----------------------------------------------------------------------- wiring: battery version
def res_h(ax, x, y, val, w=6.0, h=2.4):
    ax.add_patch(Rectangle((x, y - h / 2), w, h, fc="#f0efe9", ec="#111", lw=1, zorder=5))
    ax.text(x + w / 2, y + 2.6, val, ha="center", fontsize=8, zorder=5)


def wiring_battery():
    fig, ax = canvas(165, 150, "AirMite Battery — Seeed XIAO ESP32-C3 + SHT41 + LiPo",
                     "firmware airmite-battery   ·   i2c:  SDA = D3 / GPIO5   SCL = D4 / GPIO6   ·   "
                     "battery D1 / GPIO3   ·   USB sense D2 / GPIO4")
    left = [("D0  GPIO2", None), ("D1  GPIO3", GRN), ("D2  GPIO4", GRN), ("D3  GPIO5", BLU),
            ("D4  GPIO6", ORA), ("D5  GPIO7", None), ("D6  GPIO21", None)]
    right = [("5V", None), ("GND", BLK), ("3V3", RED), ("D10  GPIO10", None), ("D9  GPIO9", None),
             ("D8  GPIO8", None), ("D7  GPIO20", None)]
    b = dev_board(ax, 60, 96, 30, 30, "XIAO ESP32-C3", "top view, USB-C up", left, right, "IPEX antenna")
    s = sht41(ax, 120, 100)
    i2c_wires(ax, b, s, (90, 87.5, 85, 82.5), (95, 99), (56, 52), ("3V3", "GND", "D3  GPIO5", "D4  GPIO6"))
    note(ax, 4, 128, "SHT41 — four wires", "3V3          →  VIN   (never 5V)\nGND         →  GND\nD3 / GPIO5  →  SDA\nD4 / GPIO6  →  SCL")
    note(ax, 4, 104, "Not the XIAO default I2C",
         "Its default is D4/D5. AirMite uses\nD3/D4 so every variant has the same\nwiring (GPIO5/6).")

    ax.plot([4, 161], [76, 76], color="#ddd", lw=1)
    ax.text(4, 70, "Battery + charging", fontsize=13, weight="bold")
    # bottom view pads
    BX, BY = 60, 40
    board(ax, BX, BY, 30, 18, "#3a3f47", "XIAO   (BOTTOM view)", "USB-C same end")
    bp = {"B+": (BX + 9, BY + 11), "B−": (BX + 19, BY + 11)}
    for t, c, dx, ha in (("B+", "#ff8080", -3.4, "right"), ("B−", "#ffffff", 3.4, "left")):
        pad(ax, *bp[t], r=1.6)
        ax.text(bp[t][0] + dx, BY + 11, t, ha=ha, va="center", fontsize=10, weight="bold", color=c, zorder=5)
    ax.text(BX + 15, BY + 3, "solder pads on the underside", ha="center", fontsize=7.5, color="#9aa3ad", zorder=5)
    ax.add_patch(FancyBboxPatch((120, 44), 26, 15, boxstyle="round,pad=0,rounding_size=1.2",
                                fc="#e9e4d6", ec="#111", lw=1.2, zorder=4))
    ax.text(133, 61, "LiPo 3.7 V (1S)", ha="center", fontsize=11, weight="bold")
    ax.text(133, 51.5, "red = +    black = −\n~300–1000 mAh", ha="center", va="center", fontsize=8.5, color="#333", zorder=5)
    route(ax, [bp["B+"], (bp["B+"][0], BY + 14), (104, BY + 14), (104, 55), (120, 55)], RED, z=7)
    route(ax, [bp["B−"], (bp["B−"][0], BY + 6), (110, BY + 6), (110, 48), (120, 48)], BLK, z=7)
    note(ax, 4, 64, "How it charges",
         "The charger is on the XIAO: plug\nUSB-C in and the cell charges while\nthe sensor runs. With USB in it also\nstays awake (settings, updates).")

    def divider(y, src, r1, r2, tap, what, col):
        x0 = 14
        ax.text(x0 - 1.5, y, src, ha="right", va="center", fontsize=9, weight="bold", color=col)
        route(ax, [(x0, y), (x0 + 3, y)], BLK, lw=1.6); res_h(ax, x0 + 3, y, r1)
        route(ax, [(x0 + 9, y), (x0 + 15, y)], BLK, lw=1.6); res_h(ax, x0 + 15, y, r2)
        route(ax, [(x0 + 21, y), (x0 + 24, y)], BLK, lw=1.6)
        ax.text(x0 + 25, y, "GND", ha="left", va="center", fontsize=9, weight="bold")
        ax.add_patch(Circle((x0 + 12, y), 0.6, fc="#111", ec="#111", zorder=6))
        route(ax, [(x0 + 12, y), (x0 + 12, y - 4.5), (x0 + 34, y - 4.5)], GRN, lw=1.6)
        ax.text(x0 + 35, y - 4.5, tap + "   " + what, ha="left", va="center", fontsize=8.5, color=GRN, weight="bold")

    ax.text(4, 30, "Two dividers to add", fontsize=10.5, weight="bold")
    divider(22, "B+", "220k", "220k", "D1 / GPIO3", "battery voltage", RED)
    divider(10, "5V", "100k", "150k", "D2 / GPIO4", "USB plugged in", "#333")
    note(ax, 96, 30, "Before you power it",
         "•  Match + / − on the pads: reversed polarity kills the board.\n"
         "•  Never wire the cell to 5V or 3V3.\n"
         "•  Not D0 / GPIO2 for a divider: boot pin.\n"
         "•  The C3 has no PCB antenna: plug the IPEX one in.")
    save(fig, "wiring-battery.png")


# ----------------------------------------------------------------------- schematics
def sch_ic(ax, x, y, w, pins_l, pins_r, ref, name, pitch=5.0):
    """box with pin stubs; returns {pin: endpoint}"""
    n = max(len(pins_l), len(pins_r))
    h = pitch * (n + 1)
    ax.add_patch(Rectangle((x, y), w, h, fc="#fffbe8", ec="#8b0000", lw=1.4, zorder=4))
    ax.text(x + w / 2, y + h + 4.5, ref, ha="center", fontsize=9, weight="bold", color="#8b0000")
    ax.text(x + w / 2, y + h + 1.2, name, ha="center", fontsize=8, color="#555")
    pos = {}
    for side, pins in ((0, pins_l), (1, pins_r)):
        for i, p in enumerate(pins):
            if not p:
                continue
            py = y + h - pitch * (i + 1)
            x0 = x + w if side else x
            x1 = x0 + (5 if side else -5)
            ax.plot([x0, x1], [py, py], color="#8b0000", lw=1.3, zorder=4)
            ax.text(x0 + (-1 if side else 1), py, p, ha="right" if side else "left", va="center", fontsize=7.5, zorder=5)
            pos[p] = (x1, py)
    return pos


def wire(ax, pts):
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color="#006400", lw=1.3, zorder=3)


def dot(ax, p):
    ax.add_patch(Circle(p, 0.7, fc="#006400", ec="#006400", zorder=5))


def gnd(ax, p):
    x, y = p
    wire(ax, [(x, y), (x, y - 2)])
    for i, w in enumerate((3, 2, 1)):
        ax.plot([x - w, x + w], [y - 2 - i * 0.8] * 2, color="#8b0000", lw=1.3, zorder=4)


def rail(ax, p, label):
    x, y = p
    wire(ax, [(x, y), (x, y + 2)])
    ax.plot([x - 2, x + 2], [y + 2, y + 2], color="#8b0000", lw=1.3, zorder=4)
    ax.text(x, y + 3, label, ha="center", va="bottom", fontsize=8, weight="bold", color="#8b0000")


def res_v(ax, x, ytop, ref, val):
    """vertical resistor from ytop down 10 units; returns (top, bottom)"""
    ax.plot([x, x], [ytop, ytop - 2], color="#8b0000", lw=1.3)
    ax.add_patch(Rectangle((x - 1.2, ytop - 8), 2.4, 6, fc="white", ec="#8b0000", lw=1.3, zorder=4))
    ax.plot([x, x], [ytop - 8, ytop - 10], color="#8b0000", lw=1.3)
    ax.text(x + 2, ytop - 4, ref, fontsize=7.5, va="center", weight="bold")
    ax.text(x + 2, ytop - 6.5, val, fontsize=7.5, va="center")
    return (x, ytop), (x, ytop - 10)


def sht_part(ax, x, y):
    return sch_ic(ax, x, y, 18, ["VIN", "SDA", "SCL", "GND"], [], "U2", "SHT41 breakout")


def schematic_usb():
    fig, ax = canvas(130, 72, "AirMite USB — schematic", "firmware airmite-usb / airmite-usb-plus")
    u1 = sch_ic(ax, 20, 18, 22, [], ["3V3", "GPIO5", "GPIO6", "GND"], "U1", "ESP32-C3 SuperMini (Plus)")
    ax.text(31, 14, "USB-C = power", ha="center", fontsize=7.5, color="#555")
    u2 = sht_part(ax, 90, 18)
    v, g = u1["3V3"], u1["GND"]
    wire(ax, [v, (60, v[1]), u2["VIN"]]); dot(ax, (60, v[1])); rail(ax, (60, v[1]), "+3V3")
    wire(ax, [u1["GPIO5"], u2["SDA"]]); ax.text(65, u1["GPIO5"][1] + 0.8, "SDA", fontsize=7.5, color="#006400", ha="center")
    wire(ax, [u1["GPIO6"], u2["SCL"]]); ax.text(65, u1["GPIO6"][1] + 0.8, "SCL", fontsize=7.5, color="#006400", ha="center")
    wire(ax, [g, (60, g[1]), u2["GND"]]); dot(ax, (60, g[1])); gnd(ax, (60, g[1]))
    ax.text(4, 6, "The SHT41 breakout carries its own I2C pull-ups and decoupling: no other parts.", fontsize=8.5, color="#333")
    save(fig, "schematic-usb.png")


def schematic_battery():
    fig, ax = canvas(150, 100, "AirMite Battery — schematic", "firmware airmite-battery")
    P, y1, x1 = 10.0, 22.0, 70
    u1 = sch_ic(ax, x1, y1, 26, ["BAT+", "GPIO3 (D1)", "5V", "GPIO4 (D2)", "GND"],
                ["3V3", "GPIO5 (D3)", "GPIO6 (D4)"], "U1", "Seeed XIAO ESP32-C3", pitch=P)
    ax.text(x1 + 13, y1 - 4, "BAT+ / BAT− = pads under the board", ha="center", fontsize=7.5, color="#555")
    u2 = sch_ic(ax, 120, y1 + P, 18, ["VIN", "SDA", "SCL", "GND"], [], "U2", "SHT41 breakout", pitch=P)
    # I2C: straight across
    v = u1["3V3"]; wire(ax, [v, u2["VIN"]]); dot(ax, (108, v[1])); rail(ax, (108, v[1]), "+3V3")
    wire(ax, [u1["GPIO5 (D3)"], u2["SDA"]]); wire(ax, [u1["GPIO6 (D4)"], u2["SCL"]])
    g2 = u2["GND"]; wire(ax, [g2, (110, g2[1])]); gnd(ax, (110, g2[1]))
    # battery divider R1/R2 on BAT+, tap = GPIO3
    xb, pb = 40, u1["BAT+"]
    wire(ax, [pb, (xb, pb[1])]); dot(ax, (xb, pb[1]))
    _, b1 = res_v(ax, xb, pb[1], "R1", "220k")
    dot(ax, b1); wire(ax, [b1, u1["GPIO3 (D1)"]])
    _, b2 = res_v(ax, xb, b1[1], "R2", "220k"); gnd(ax, b2)
    # cell
    xc = 18
    wire(ax, [(xb, pb[1]), (xc, pb[1]), (xc, pb[1] - 8)])
    ax.plot([xc - 3, xc + 3], [pb[1] - 8] * 2, color="#8b0000", lw=1.6)
    ax.plot([xc - 1.5, xc + 1.5], [pb[1] - 9.5] * 2, color="#8b0000", lw=2.6)
    ax.plot([xc, xc], [pb[1] - 9.5, pb[1] - 12], color="#8b0000", lw=1.3); gnd(ax, (xc, pb[1] - 12))
    ax.text(xc + 4, pb[1] - 9, "BT1\nLiPo 1S", fontsize=7.5, va="center", weight="bold")
    ax.text(xc - 4, pb[1] - 7.5, "+", fontsize=9, ha="center", color="#8b0000")
    # USB sense divider R3/R4 on 5V, tap = GPIO4, bottom = board GND
    xa, p5 = 56, u1["5V"]
    wire(ax, [p5, (xa, p5[1])])
    ax.text(xa - 1, p5[1] + 1, "+5V (USB)", ha="right", fontsize=7.5, weight="bold", color="#8b0000")
    _, b3 = res_v(ax, xa, p5[1], "R3", "100k")
    dot(ax, b3); wire(ax, [b3, u1["GPIO4 (D2)"]])
    _, b4 = res_v(ax, xa, b3[1], "R4", "150k")
    wire(ax, [b4, u1["GND"]]); dot(ax, b4); gnd(ax, b4)
    note(ax, 4, 14, "Notes",
         "R1/R2: battery voltage (firmware factor 2.0 = 220k/220k; set another in HA if you use other values).\n"
         "R3/R4: USB plugged in -> the sensor stays awake. The XIAO charges BT1 by itself.")
    save(fig, "schematic-battery.png")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    wiring_usb(); wiring_battery(); schematic_usb(); schematic_battery()
