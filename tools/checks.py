"""Kontrole spójności repozytorium.

    python tools/checks.py sheet arkusz.csv          # walidacja arkusza annotacji względem schema.yaml
    python tools/checks.py consistency               # schema.yaml vs 02_codebook_v0.1.md vs szablon CSV
    python tools/checks.py placeholders              # placeholdery w *.md vs rejestr (00_rejestr_...)

Placeholder ma postać {{Pnn: opis | zależy od: ... | domyślnie: ...}}; rejestr to tabela w pliku 00_rejestr*.md.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "tools" / "schema.yaml"
PLACEHOLDER_RE = re.compile(r"\{\{(P\d{2})\b[^}]*\}\}")
REGISTRY_ROW_RE = re.compile(r"^\|\s*(P\d{2})\s*\|")


def load_schema(path: Path = SCHEMA) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def validate_sheet_rows(rows: list[dict], schema: dict, allow_l2: bool = False) -> list[str]:
    """Zwraca listę błędów (pusta = OK). Puste komórki są dozwolone (nie zakodowano jeszcze), wartości spoza listy nie."""
    errors = []
    vars_ = schema["variables"]
    for i, r in enumerate(rows, start=2):  # wiersz 1 = nagłówek
        for name, spec in vars_.items():
            if name not in r:
                continue
            v = (r[name] or "").strip()
            if v == "":
                continue
            if spec["level"] == "L2" and not allow_l2:
                errors.append(f"wiersz {i}: zmienna poziomu L2 '{name}' wypełniona, ale D1 nie potwierdzono (użyj --allow-l2)")
                continue
            if spec["values"] != "free_text" and v not in spec["values"]:
                errors.append(f"wiersz {i}: '{name}'='{v}' spoza dozwolonych {spec['values']}")
        cm = (r.get("celeb_mention") or "").strip()
        cid = (r.get("celeb_id") or "").strip()
        if cm in ("explicit_name", "implied") and not cid:
            errors.append(f"wiersz {i}: celeb_mention={cm}, ale celeb_id puste")
        if cm == "none" and cid and cid != "na":
            errors.append(f"wiersz {i}: celeb_mention=none, a celeb_id='{cid}'")
    return errors


def check_consistency(root: Path = ROOT) -> list[str]:
    schema = load_schema(root / "tools" / "schema.yaml")
    errors = []
    codebook = next(iter(sorted(root.glob("02_codebook*.md"))), None)
    if codebook is None:
        return ["brak pliku 02_codebook*.md"]
    text = codebook.read_text(encoding="utf-8")
    for name, spec in schema["variables"].items():
        if f"`{name}`" not in text:
            errors.append(f"zmienna `{name}` ze schematu nie występuje w {codebook.name}")
            continue
        if spec["values"] != "free_text":
            for val in spec["values"]:
                if f"`{val}`" not in text:
                    errors.append(f"wartość `{val}` zmiennej {name} nie występuje w {codebook.name}")
    tpl = root / "templates" / "annotation_sheet_template.csv"
    if tpl.exists():
        header = tpl.read_text(encoding="utf-8").splitlines()[0].split(",")
        expected = schema["annotation_sheet_columns"][:3] + list(schema["variables"]) + schema["annotation_sheet_columns"][3:]
        missing = [c for c in expected if c not in header]
        if missing:
            errors.append(f"szablon CSV nie ma kolumn: {missing}")
    else:
        errors.append("brak templates/annotation_sheet_template.csv")
    return errors


def check_placeholders(root: Path = ROOT) -> tuple[list[str], dict]:
    reg_file = next(iter(sorted(root.glob("00_rejestr*.md"))), None)
    if reg_file is None:
        return ["brak pliku 00_rejestr*.md"], {}
    registry = {}
    for line in reg_file.read_text(encoding="utf-8").splitlines():
        m = REGISTRY_ROW_RE.match(line)
        if m:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            registry[m.group(1)] = cells
    used = Counter()
    for f in sorted(root.glob("[0-9][0-9]_*.md")):
        if f == reg_file:
            continue
        for m in PLACEHOLDER_RE.finditer(f.read_text(encoding="utf-8")):
            used[m.group(1)] += 1
    errors = [f"placeholder {p} użyty w dokumentach, ale nie ma go w rejestrze" for p in used if p not in registry]
    stats = {"registry": len(registry), "used_ids": len(used), "occurrences": sum(used.values()),
             "unused_in_docs": sorted(set(registry) - set(used))}
    return errors, stats


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sheet"); s.add_argument("csv"); s.add_argument("--allow-l2", action="store_true")
    sub.add_parser("consistency"); sub.add_parser("placeholders")
    a = p.parse_args(argv)
    if a.cmd == "sheet":
        with open(a.csv, encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        errs = validate_sheet_rows(rows, load_schema(), allow_l2=a.allow_l2)
        print("\n".join(errs) if errs else f"OK: {len(rows)} wierszy")
        sys.exit(1 if errs else 0)
    if a.cmd == "consistency":
        errs = check_consistency()
        print("\n".join(errs) if errs else "OK: schema, codebook i szablon CSV spójne")
        sys.exit(1 if errs else 0)
    if a.cmd == "placeholders":
        errs, stats = check_placeholders()
        print("\n".join(errs) if errs else "OK: wszystkie użyte placeholdery są w rejestrze")
        print(stats)
        sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
