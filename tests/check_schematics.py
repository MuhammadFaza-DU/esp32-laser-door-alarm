"""Check the actual KiCad and EasyEDA wires against the breadboard wiring."""

import json
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    frozenset(items.split()) for items in [
        "U1:3V3 D1:1 R2:1",
        "U1:34 D1:2 R1:1",
        "U1:21 R2:2 SW1:1",
        "U1:22 R3:1",
        "U1:VIN BZ1:1 D2:1",
        "U1:GND R1:2 SW1:2 R4:2 Q1:1",
        "BZ1:2 D2:2 Q1:3",
        "Q1:2 R3:2 R4:1",
    ]
}


def nets(wires, labels, pins):
    neighbors = defaultdict(set)
    names = {}
    for a, b in wires:
        neighbors[a].add(b)
        neighbors[b].add(a)
    for point, label in labels:
        if label in names:
            neighbors[point].add(names[label])
            neighbors[names[label]].add(point)
        names[label] = point
    pending = set(pins)
    groups = set()
    while pending:
        seen = {pending.pop()}
        stack = list(seen)
        while stack:
            for node in neighbors[stack.pop()] - seen:
                seen.add(node)
                stack.append(node)
        pending -= seen
        groups.add(frozenset(pins[node] for node in seen if node in pins))
    assert groups == EXPECTED, f"missing {EXPECTED - groups}; extra {groups - EXPECTED}"


def parse_sexp(data):
    stack = [[]]
    for tok in re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', data):
        if tok == "(":
            stack.append([])
        elif tok == ")":
            child = stack.pop()
            stack[-1].append(child)
        else:
            stack[-1].append(json.loads(tok) if tok.startswith('"') else tok)
    assert len(stack) == 1 and len(stack[0]) == 1
    return stack[0][0]


def nodes(node, name):
    return [child for child in node if isinstance(child, list) and child[0] == name]


def node(parent, name):
    return next(iter(nodes(parent, name)))


def kcoords(form):
    return tuple(round(float(v) / 1.27) for v in form[1:3])


def check_kicad():
    schematic = parse_sexp((ROOT / "hardware/kicad/door-alarm.kicad_sch").read_text(encoding="utf-8"))
    lib = {item[1]: item for item in nodes(node(schematic, "lib_symbols"), "symbol")}
    wires = [[kcoords(pt) for pt in node(w, "pts")[1:]] for w in nodes(schematic, "wire")]
    labels = [(kcoords(node(l, "at")), l[1]) for l in nodes(schematic, "label")]
    pins = {}
    for s in nodes(schematic, "symbol"):
        x, y = kcoords(node(s, "at"))
        assert node(s, "at")[3] == "0"
        ref = next(prop[2] for prop in nodes(s, "property") if prop[1] == "Reference")
        for section in nodes(lib[node(s, "lib_id")[1]], "symbol"):
            for pin in nodes(section, "pin"):
                dx, dy = kcoords(node(pin, "at"))
                key = (x + dx, y - dy)
                assert key not in pins
                pins[key] = f"{ref}:{node(pin, 'number')[1]}"
    nets(wires, labels, pins)
    print("PASS: KiCad connectivity and diode polarity")


def check_easyeda():
    doc = json.loads((ROOT / "hardware/easyeda/door-alarm.json").read_text(encoding="utf-8"))
    assert doc["head"]["docType"] == "1"
    wires, labels, pins = [], [], {}
    for shape in doc["shape"]:
        items = shape.split("~")
        if items[0] == "W":
            x1, y1, x2, y2 = map(int, items[1].split())
            wires.append(((x1, y1), (x2, y2)))
        if items[0] == "N":
            labels.append(((int(items[1]), int(items[2])), items[5]))
        if items[0] == "LIB":
            parts = shape.split("#@$")[1:]
            ref = next(p.split("~")[12] for p in parts if p.startswith("T~P~"))
            for pin in (p for p in parts if p.startswith("P~")):
                raw, dot, *_ = pin.split("^^")
                key = tuple(int(v) for v in dot.split("~"))
                assert key not in pins
                pins[key] = f"{ref}:{raw.split('~')[3]}"
    nets(wires, labels, pins)
    print("PASS: EasyEDA connectivity and diode polarity")


def check_artifacts():
    svg = ET.parse(ROOT / "docs/diagrams/door-alarm.svg")
    assert svg.getroot().tag.endswith("}svg")
    diagram = json.loads((ROOT / "wokwi/diagram.json").read_text(encoding="utf-8"))
    ids = {part["id"] for part in diagram["parts"]}
    for a, b, *_ in diagram["connections"]:
        assert a.split(":")[0] in ids and b.split(":")[0] in ids
    sim = (ROOT / "wokwi/sketch.ino").read_text(encoding="utf-8")
    real = (ROOT / "firmware/DoorAlarm/DoorAlarm.ino").read_text(encoding="utf-8")
    assert sim.replace(
        "INPUT_PULLUP);  // Simulasi tidak memakai pull-up eksternal.",
        "INPUT);  // Pull-up eksternal 10 kΩ ke 3V3.",
    ) == real
    print("PASS: SVG parses; Wokwi IDs resolve and the only firmware difference is pull-up mode")


if __name__ == "__main__":
    check_kicad()
    check_easyeda()
    check_artifacts()
