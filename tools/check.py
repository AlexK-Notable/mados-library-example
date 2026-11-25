#!/usr/bin/env python3
"""Check that every folder in this repository is laid out the way the kit builder reads it.

    python3 tools/check.py

It needs nothing but Python. GitHub runs it after every upload (.github/workflows/check.yml):
a green tick next to the upload means the files are in order, a red cross means something
listed below needs fixing. It reads file names and the small text files only; it never opens
a model in CAD software, and it changes nothing.
"""
import json
import pathlib
import re
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CATEGORIES = ("Blocks", "Twist blocks", "Mini blocks", "Joiners", "Covers", "Hinges", "Braces", "Plates", "Hardware")
PART_NUMBER = re.compile(r"MADOS-[0-9]{2}[A-Z]{2}$")
SLUG = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*$")
BUILDER_MADE = re.compile(r"(channel|twist|cover|hinge|wrap)_[a-z0-9_.x-]+$")     # sizes the builder makes itself
problems, notes = [], []


def problem(where, text):
    problems.append(f"{where.relative_to(ROOT)}: {text}")


def read_text_file(path, required, optional):
    """A text file of `key: value` lines. Returns the values, or None if the file is missing."""
    if not path.is_file():
        problem(path.parent, f"there is no {path.name}")
        return None
    values = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, colon, value = line.partition(":")
        key, value = key.strip(), value.strip()
        if not colon or not key or not value:
            problem(path, f"line {number} is not `key: value`: {line.strip()!r}")
        elif key in values:
            problem(path, f"`{key}` appears twice")
        elif key not in required and key not in optional:
            problem(path, f"line {number}: `{key}` is not a key this file uses (known keys: {', '.join(required + optional)})")
        else:
            values[key] = value
    for key in required:
        if key not in values:
            problem(path, f"`{key}:` is missing")
    return values


def check_stl(path):
    size = path.stat().st_size
    with open(path, "rb") as f:
        head = f.read(84)
    if head[:5] == b"solid" and size != 84 + 50 * struct.unpack("<I", head[80:84])[0]:
        return                                        # a text STL: fine
    if size < 84 or size != 84 + 50 * struct.unpack("<I", head[80:84])[0]:
        problem(path, "is not a complete STL file (the upload may have been cut short)")


def check_models(folder, stem):
    """The model files of one part: <stem>[-<strength>]_CAD.step, <stem>[-<strength>]_Recommended.stl
    and, optionally, <stem>-<strength>.stl for the other strengths."""
    cad, recommended, strengths = [], [], {}
    for path in sorted(folder.iterdir()):
        name = path.name
        if name == "part.txt" or name.lower() in ("readme.md", "picture.webp", "picture.png", "picture.jpg"):
            continue
        if path.is_dir():
            problem(path, "a part's folder holds files only, no folders")
            continue
        if name != name.strip() or " " in name:
            problem(path, "has a space in its name")
            continue
        if path.stat().st_size == 0:
            problem(path, "is empty")
            continue
        m = re.fullmatch(re.escape(stem) + r"(?:-([0-9]))?(_CAD\.step|_Recommended\.stl|\.stl)", name)
        if not m:
            problem(path, f"is not a file name this folder uses. Expected {stem}_CAD.step, {stem}_Recommended.stl, "
                          f"or with a strength: {stem}-3_CAD.step, {stem}-1_Recommended.stl, {stem}-0.stl ... {stem}-9.stl")
            continue
        strength, kind = m.group(1), m.group(2)
        if kind == "_CAD.step":
            cad.append(path)
            if b"ISO-10303-21" not in path.open("rb").read(64):
                problem(path, "does not start like a STEP file")
        else:
            check_stl(path)
            if kind == "_Recommended.stl":
                recommended.append((path, strength))
            if strength is None and kind == ".stl":
                problem(path, f"needs either a strength ({stem}-3.stl) or _Recommended in its name")
            elif strength is not None:
                if strength in strengths:
                    problem(path, f"strength {strength} is here twice ({strengths[strength].name})")
                strengths[strength] = path
    if len(cad) != 1:
        problem(folder, f"needs exactly one _CAD.step file, and has {len(cad)}")
    if len(recommended) != 1:
        problem(folder, f"needs exactly one _Recommended.stl file, and has {len(recommended)}")
    elif strengths and recommended[0][1] is None:
        problem(recommended[0][0], "this part has strengths, so the recommended file needs its strength in the name too")
    if strengths and len(strengths) not in (1, 10):
        missing = [s for s in "0123456789" if s not in strengths]
        notes.append(f"{folder.relative_to(ROOT)}: strengths {', '.join(missing)} are not here; the builder will offer only the ones that are")


def check_part(folder, stem, community=False):
    required = ["name", "category", "description"] + (["author", "licence"] if community else [])
    optional = ["mass_g", "layer_height", "page", "family", "position"] + ([] if community else ["author", "licence"])
    values = read_text_file(folder / "part.txt", required, optional)
    if values:
        if values.get("category") and values["category"] not in CATEGORIES:
            problem(folder / "part.txt", f"category `{values['category']}` is not one of: {', '.join(CATEGORIES)}. "
                                         "A new category is fine: add it to CATEGORIES in tools/check.py")
        if "mass_g" in values and not re.fullmatch(r"[0-9]+(\.[0-9]+)?", values["mass_g"]):
            problem(folder / "part.txt", f"mass_g is a number of grams, such as 3.5 (it says {values['mass_g']!r})")
        if "page" in values and not values["page"].startswith("https://"):
            problem(folder / "part.txt", "page is a full web address starting https://")
    check_models(folder, stem)


def folders(path):
    return sorted(p for p in path.iterdir() if p.is_dir() and not p.name.startswith(".")) if path.is_dir() else []


known = set()
for folder in folders(ROOT / "parts"):
    if not PART_NUMBER.match(folder.name):
        problem(folder, "an official part's folder is named after its part number, such as MADOS-20AA")
        continue
    known.add(folder.name)
    check_part(folder, folder.name)

for maker in folders(ROOT / "community"):
    if not SLUG.match(maker.name):
        problem(maker, "a maker's folder name is lower case letters, numbers and dashes, such as jane-smith")
        continue
    for folder in folders(maker):
        if not SLUG.match(folder.name):
            problem(folder, "a community part's folder name is lower case letters, numbers and dashes, such as corner-shelf")
            continue
        known.add(f"{maker.name}/{folder.name}")
        check_part(folder, folder.name, community=True)

for folder in folders(ROOT / "sections"):
    if not SLUG.match(folder.name):
        problem(folder, "a section's folder name is lower case letters, numbers and dashes, such as plain-block-end")
        continue
    check_part(folder, folder.name)

for folder in folders(ROOT / "assemblies"):
    if not SLUG.match(folder.name):
        problem(folder, "an assembly's folder name is lower case letters, numbers and dashes, such as desk-shelf")
        continue
    read_text_file(folder / "assembly.txt", ["title", "author", "licence", "description"], ["page"])
    build = folder / "build.json"
    if not build.is_file():
        problem(folder, "there is no build.json (the file the kit builder's Save button gives)")
        continue
    try:
        data = json.loads(build.read_text(encoding="utf-8"))
        assert data.get("format") == "mados-kit build" and isinstance(data.get("items"), list) and data["items"]
    except Exception:
        problem(build, "is not a build saved from the kit builder")
        continue
    elsewhere = sorted({i.get("name", "?") for i in data["items"]} - known)
    elsewhere = [n for n in elsewhere if not BUILDER_MADE.match(n)]
    if elsewhere:
        notes.append(f"{build.relative_to(ROOT)}: uses parts whose files are not in this repository: {', '.join(elsewhere)}")
    for extra in sorted(p.name for p in folder.iterdir() if p.name not in ("assembly.txt", "build.json") and not p.name.startswith("picture.")):
        problem(folder / extra, "an assembly's folder holds assembly.txt, build.json and optionally picture.webp/.png/.jpg")

filaments = ROOT / "filaments.csv"
if filaments.is_file():
    rows = filaments.read_text(encoding="utf-8").splitlines()
    if not rows or rows[0].strip() != "filament,adjustment,notes":
        problem(filaments, "the first line is: filament,adjustment,notes")
    seen = set()
    for number, row in enumerate(rows[1:], 2):
        if not row.strip():
            continue
        cells = row.split(",", 2)
        if len(cells) < 2 or not cells[0].strip() or not re.fullmatch(r"[+-]?[0-9]", cells[1].strip()):
            problem(filaments, f"line {number} is not `filament name,adjustment,notes` with an adjustment such as +2, 0 or -1: {row!r}")
        elif cells[0].strip().lower() in seen:
            problem(filaments, f"line {number}: {cells[0].strip()} is listed twice")
        else:
            seen.add(cells[0].strip().lower())

for text in notes:
    print("note     " + text)
for text in problems:
    print("PROBLEM  " + text)
print(f"\n{len(known)} parts checked, {len(problems)} problem(s), {len(notes)} note(s)")
sys.exit(1 if problems else 0)
