"""Generate the three physical schematic formats from one drawing and net model."""

import json
import uuid
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MM = 1.27
SVG = 5
INWARD = {"r": (1, 0), "l": (-1, 0), "d": (0, 1), "u": (0, -1)}
KANGLE = {"r": 0, "l": 180, "d": 270, "u": 90}
EANGLE = {"r": 180, "l": 0, "d": 90, "u": 270}


def poly(*points):
    return points


resistor = [poly((0, -3), (2, -3), (2, 3), (-2, 3), (-2, -3), (0, -3))]
vertical = [("1", "1", 0, -6, "d", 3, "passive"),
            ("2", "2", 0, 6, "u", 3, "passive")]
horizontal = [("1", "1", -6, 0, "r", 3, "passive"),
              ("2", "2", 6, 0, "l", 3, "passive")]
diode = [
    poly((-3, -3), (3, -3)),
    poly((0, -3), (-3, 3), (3, 3), (0, -3)),
]
buzzer = [
    poly((0, -3), (2, -3), (2, 3), (0, 3)),
    poly((2, -2), (4, -2), (6, -4), (6, 4), (4, 2), (2, 2)),
]
devkit = [poly((-14, -22), (14, -22), (14, 22), (-14, 22), (-14, -22))]

# Pin tuples: number, label, connection point, inward direction, length, electrical type.
SYMBOLS = {
    "Board": (devkit, [
        ("3V3", "3V3", -20, -15, "r", 6, "power_out"),
        ("34", "D34", -20, -5, "r", 6, "input"),
        ("21", "D21", -20, 5, "r", 6, "input"),
        ("22", "D22", 20, 0, "l", 6, "output"),
        ("VIN", "VIN", 20, -15, "l", 6, "power_out"),
        ("GND", "GND", 20, 15, "l", 6, "power_out"),
    ]),
    "ResistorV": (resistor, vertical),
    "ResistorH": ([tuple((y, -x) for x, y in p) for p in resistor], horizontal),
    "Photodiode": (diode + [
        poly((-8, -3), (-4, -1), (-5, -3)),
        poly((-7, 1), (-3, 3), (-4, 1)),
    ], [("1", "K", 0, -6, "d", 3, "passive"), ("2", "A", 0, 6, "u", 3, "passive")]),
    "Diode": (diode, [("1", "K", 0, -6, "d", 3, "passive"),
                      ("2", "A", 0, 6, "u", 3, "passive")]),
    "Buzzer": (buzzer + [poly((-3, -4), (-3, -2)), poly((-4, -3), (-2, -3))],
               [("1", "+", 0, -6, "d", 3, "passive"), ("2", "-", 0, 6, "u", 3, "passive")]),
    "Switch": ([poly((0, -3), (0, -2)), poly((0, 3), (0, 2)), poly((0, 2), (3, -2))],
               vertical),
    "NPN": ([
        poly((-5, 0), (-1, 0)), poly((-1, -4), (-1, 4)),
        poly((-1, -2), (3, -5)), poly((-1, 2), (3, 5)),
        poly((0, 4), (3, 5), (2, 2)),
    ], [
        ("1", "E", 3, 7, "u", 2, "passive"),
        ("2", "B", -9, 0, "r", 4, "input"),
        ("3", "C", 3, -7, "d", 2, "passive"),
    ]),
}

# (reference, value, symbol, origin, top-left value-label position)
PARTS = [
    ("U1", "ESP32-WROOM-32 DevKit", "Board", (104, 74), (88, 48)),
    ("D1", "Fotodioda Si", "Photodiode", (31, 45), (39, 46)),
    ("R1", "47 kΩ", "ResistorV", (31, 69), (39, 69)),
    ("R2", "10 kΩ", "ResistorV", (29, 108), (38, 108)),
    ("SW1", "Switch button", "Switch", (29, 129), (38, 129)),
    ("BZ1", "TMB12A05", "Buzzer", (175, 50), (150, 50)),
    ("D2", "Dioda pelindung", "Diode", (198, 50), (202, 56)),
    ("R3", "680 Ω", "ResistorH", (141, 103), (134, 96)),
    ("R4", "100 kΩ", "ResistorV", (154, 116), (133, 116)),
    ("Q1", "KN2222A", "NPN", (172, 103), (181, 103)),
]

PATHS = [
    [(31, 32), (31, 39)], [(31, 51), (31, 58), (31, 63)],
    [(31, 58), (61, 58)], [(31, 75), (31, 81)],
    [(29, 96), (29, 102)], [(29, 114), (29, 119), (29, 123)],
    [(29, 119), (61, 119)], [(29, 135), (29, 140)],
    [(74, 59), (84, 59)], [(74, 69), (84, 69)], [(74, 79), (84, 79)],
    [(124, 59), (132, 59)], [(124, 74), (132, 74)], [(124, 89), (132, 89)],
    [(175, 34), (175, 39), (175, 44)], [(175, 39), (198, 39), (198, 44)],
    [(175, 56), (175, 65), (175, 96)], [(198, 56), (198, 65), (175, 65)],
    [(128, 103), (135, 103)], [(147, 103), (154, 103), (163, 103)],
    [(154, 103), (154, 110)], [(154, 122), (154, 132)], [(175, 110), (175, 132)],
]
NET_LABELS = [
    ((31, 32), "3V3"), ((61, 58), "D34"), ((31, 81), "GND"),
    ((29, 96), "3V3"), ((61, 119), "D21"), ((29, 140), "GND"),
    ((74, 59), "3V3"), ((74, 69), "D34"), ((74, 79), "D21"),
    ((132, 59), "VIN"), ((132, 74), "D22"), ((132, 89), "GND"),
    ((175, 34), "VIN"), ((128, 103), "D22"), ((154, 132), "GND"), ((175, 132), "GND"),
]
JOINTS = [(31, 58), (29, 119), (175, 39), (175, 65), (154, 103)]
HEADINGS = [
    (8, 23, "01  Penerima berkas"),
    (8, 90, "02  Switch button"),
    (145, 23, "03  Driver buzzer"),
]
NOTES = [
    (8, 28, "Laser merah → D1 (optik)"),
    (145, 28, "VIN diukur 4,5 V saat buzzer diuji."),
    (178, 70, "Garis dioda ke VIN"),
    (185, 111, "B ← D22"),
    (185, 118, "E → GND"),
    (185, 125, "C → BZ1 negatif"),
    (85, 104, "USB-C menyuplai board."),
    (85, 109, "VIN ≠ 3V3."),
    (8, 150, "Prototipe meja | Laser tidak terhubung secara listrik ke ESP32."),
]


def q(text):
    return json.dumps(text, ensure_ascii=False)


def uid(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "esp32-laser-door-alarm/" + str(name)))


def mm(value):
    return f"{value * MM:.4f}".rstrip("0").rstrip(".") if value else "0"


def kxy(p, flip=False):
    x, y = p
    return f"{mm(x)} {mm(-y if flip else y)}"


def effects(size, extra=""):
    return f"(effects (font (size {size} {size})) {extra})"


def kicad():
    root = uid("root")
    result = [
        '(kicad_sch (version 20231120) (generator "door_alarm")',
        f' (uuid "{root}") (paper "A4")',
        ' (title_block (title "Alarm pintu ESP32") (rev "1.0"))',
        ' (lib_symbols',
    ]
    for name, (art, pins) in SYMBOLS.items():
        names = "(pin_names (offset 0.8))" if name == "Board" else "(pin_names hide)"
        result += [
            f'  (symbol "DoorAlarm:{name}" (pin_numbers hide) {names} (exclude_from_sim no) (in_bom yes) (on_board yes)',
            f'   (property "Reference" "U" (at 0 0 0) {effects(1.2)})',
            f'   (property "Value" "{name}" (at 0 0 0) {effects(1.2)})',
            f'   (symbol "{name}_0_1"',
        ]
        for line in art:
            pts = " ".join(f"(xy {kxy(pt, flip=True)})" for pt in line)
            result.append(f"    (polyline (pts {pts}) (stroke (width 0.254) (type default)) (fill (type none)))")
        result += [f'   ) (symbol "{name}_1_1"']
        for n, pin, x, y, d, length, role in pins:
            result.append(f'    (pin {role} line (at {kxy((x, y), True)} {KANGLE[d]})'
                          f' (length {mm(length)}) (name {q(pin)} {effects(1.02)})'
                          f' (number {q(n)} {effects(1.02)}))')
        result += ["   ))"]
    result.append(" )")

    def text(x, y, words, size):
        return f' (text {q(words)} (at {kxy((x,y))} 0) {effects(size, "(justify left)")} (uuid "{uid(words + str((x,y)))}"))'

    result.append(text(8, 12, "ALARM PINTU ESP32", 3.0))
    for x, y, label in HEADINGS:
        result.append(text(x, y, label, 1.9))
    for x, y, label in NOTES:
        result.append(text(x, y, label, 1.1))
    for a, b in (p for path in PATHS for p in zip(path, path[1:])):
        result.append(f' (wire (pts (xy {kxy(a)}) (xy {kxy(b)})) (stroke (width 0) (type default)) (uuid "{uid((a,b))}"))')
    for x, y in JOINTS:
        result.append(f' (junction (at {kxy((x,y))}) (diameter 0) (color 0 0 0 0) (uuid "{uid(("joint",x,y))}"))')
    for p, label in NET_LABELS:
        result.append(f' (label "{label}" (at {kxy(p)} 0) {effects(1.1, "(justify left bottom)")} (uuid "{uid((p,label))}"))')
    for ref, value, lib, p, (x, y) in PARTS:
        result += [
            f' (symbol (lib_id "DoorAlarm:{lib}") (at {kxy(p)} 0) (unit 1)'
            f' (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{uid(ref)}")',
            f'  (property "Reference" "{ref}" (at {kxy((x,y-2.2))} 0) {effects(1.18, "(justify left)")})',
            f'  (property "Value" {q(value)} (at {kxy((x,y))} 0) {effects(1.18, "(justify left)")})',
        ]
        for n, *_ in SYMBOLS[lib][1]:
            result.append(f'  (pin {q(n)} (uuid "{uid((ref,n))}"))')
        result.append(f'  (instances (project "door-alarm" (path "/{root}" (reference "{ref}") (unit 1)))))')
    result += [' (sheet_instances (path "/" (page "1")))', ")"]
    return "\n".join(result) + "\n"


def easyeda():
    num = 0

    def eid():
        nonlocal num
        num += 1
        return f"gge{num}"

    def txt(x, y, words, kind="L", size=10, color="#183349"):
        return f"T~{kind}~{x * 10:g}~{y * 10:g}~0~{color}~Arial~{size}pt~~~~comment~{words}~1~start~{eid()}"

    shapes = [txt(8, 12, "ALARM PINTU ESP32", size=22)]
    shapes.extend(txt(x, y, t, size=15) for x, y, t in HEADINGS)
    shapes.extend(txt(x, y, t) for x, y, t in NOTES)
    for path in PATHS:
        for a, b in zip(path, path[1:]):
            pts = " ".join(f"{x * 10} {y * 10}" for x, y in (a, b))
            shapes.append(f"W~{pts}~#008800~2~0~none~{eid()}")
    for x, y in JOINTS:
        shapes.append(f"J~{x * 10}~{y * 10}~3~#008800~{eid()}")
    for (x, y), label in NET_LABELS:
        shapes.append(f"N~{x * 10}~{y * 10}~0~#006666~{label}~{eid()}~start~{x * 10 + 2}~{y * 10 - 4}~Arial~11pt~0")

    for ref, value, lib, (x, y), (tx, ty) in PARTS:
        art, pins = SYMBOLS[lib]
        parts = [f"LIB~{x * 10}~{y * 10}~package`{lib}`nameAlias`Name`Name`{value}`~~0~{eid()}"]
        parts += [txt(tx, ty - 2.2, ref, "P"), txt(tx, ty, value, "N")]
        for line in art:
            pts = " ".join(f"{(x+a) * 10} {(y+b) * 10}" for a, b in line)
            parts.append(f"PL~{pts}~#183349~2~0~none~{eid()}")
        for n, name, px, py, d, length, role in pins:
            sx, sy = (x + px) * 10, (y + py) * 10
            vx, vy = INWARD[d]
            ex, ey = sx + vx * length * 10, sy + vy * length * 10
            display = 1 if lib == "Board" else 0
            anchor = "end" if d == "l" else "start"
            name_x = ex + vx * 5
            parts.append(f"P~show~0~{n}~{sx}~{sy}~{EANGLE[d]}~{eid()}^^{sx}~{sy}"
                         f"^^M {sx} {sy} L {ex} {ey}~#183349"
                         f"^^{display}~{name_x}~{ey+3}~0~{name}~{anchor}~Arial~10pt"
                         f"^^0~{sx}~{sy}~0~{n}~start~Arial~9pt^^^^")
        shapes.append("#@$".join(parts))
    return json.dumps({
        "head": {"docType": "1", "editorVersion": "6.5.0", "x": 0, "y": 0, "c_para": {}},
        "canvas": "CA~2250~1580~#FFFFFF~yes~#CCCCCC~10~2250~1580~line~10~pixel~5~0~0",
        "shape": shapes, "BBox": {"x": 60, "y": 70, "width": 2070, "height": 1450},
        "colors": {},
    }, indent=2, ensure_ascii=False) + "\n"


def svg():
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1125 790" role="img" aria-labelledby="title desc">',
        '<title id="title">Skematik alarm pintu ESP32</title>',
        '<desc id="desc">Fotodioda ke D34, switch button ke D21, buzzer melalui KN2222A ke D22. Laser hanya terhubung secara optik.</desc>',
        '<rect width="1125" height="790" fill="#fff"/>',
        '<style>text{font-family:system-ui,sans-serif;fill:#183047} .wire{stroke:#007567;stroke-width:2.1;fill:none;stroke-linejoin:round} .part{stroke:#183047;stroke-width:2;fill:none;stroke-linejoin:round} .net{fill:#006759;font:600 12px ui-monospace,monospace} .note{font-size:11px} .ref{font:600 11px ui-monospace,monospace} .heading{font-weight:650;font-size:16px}</style>',
        '<path d="M40 77H1085 M40 722H1085" stroke="#c5d2d7"/>',
    ]

    def label(x, y, text, css="", **attrs):
        props = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
        lines.append(f'<text x="{x*SVG:g}" y="{y*SVG:g}" class="{css}" {props}>{escape(text)}</text>')

    def draw(points, css):
        pts = " ".join(f"{x*SVG:g},{y*SVG:g}" for x, y in points)
        lines.append(f'<polyline class="{css}" points="{pts}"/>')

    label(8, 12, "Alarm pintu ESP32", font_size=29, font_weight=750)
    label(217, 12, "SKEMATIK · PROTOTIPE MEJA", "net", text_anchor="end")
    for x, y, heading in HEADINGS:
        label(x, y, heading, "heading")
    for x, y, note in NOTES:
        label(x, y, note, "note")
    label(217, 150, "GPIO 34 / 21 / 22", "net", text_anchor="end")
    for path in PATHS:
        draw(path, "wire")
    for x, y in JOINTS:
        lines.append(f'<circle cx="{x*SVG}" cy="{y*SVG}" r="3.3" fill="#007567"/>')
    for (x, y), name in NET_LABELS:
        label(x, y - 0.65, name, "net")
    for ref, value, lib, (x, y), (tx, ty) in PARTS:
        art, pins = SYMBOLS[lib]
        for contour in art:
            draw([(x+a, y+b) for a, b in contour], "part")
        for _, name, a, b, d, length, _ in pins:
            vx, vy = INWARD[d]
            ex, ey = x+a+vx*length, y+b+vy*length
            draw([(x+a, y+b), (ex, ey)], "part")
            if lib == "Board":
                label(ex + vx * 1.1, ey + 0.85, name, "ref",
                      text_anchor="start" if vx > 0 else "end")
        label(tx, ty - 2.3, ref, "ref")
        label(tx, ty + 0.4, value, "note")
    return "\n".join(lines + ["</svg>", ""])


def main():
    for relative, content in [
        ("hardware/kicad/door-alarm.kicad_sch", kicad()),
        ("hardware/easyeda/door-alarm.json", easyeda()),
        ("docs/diagrams/door-alarm.svg", svg()),
    ]:
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
