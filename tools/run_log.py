"""Dziennik uruchomień instrumentu (JSONL): kto, kiedy, jaki model/wersja/parametry, jaki prompt (hash), jakie dane (hash).

Po co: wyniki modeli dostępnych przez API zmieniają się w czasie (wersje, wycofywanie), a wnioski zależą od
konfiguracji [@baumann2025]; odtwarzalność wymaga zapisu pełnej konfiguracji każdego uruchomienia.

Użycie:
    python tools/run_log.py --log runs/runs.jsonl --who imie --model NAZWA --version WERSJA \
        --params '{"temperature":0}' --prompt prompts/prompt_v1.txt --input dane/proba.csv \
        --seed 42 --codebook 02_codebook_v0.1.md --notes "pilotaż"
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import platform
from pathlib import Path


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def log_run(log_path: str, who: str, model: str, version: str, params: dict, prompt_file: str,
            input_file: str, seed, codebook_file: str | None = None, notes: str = "") -> dict:
    rec = {
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "who": who, "model": model, "model_version": version, "params": params, "seed": seed,
        "prompt_file": prompt_file, "prompt_sha256": sha256_file(prompt_file),
        "input_file": input_file, "input_sha256": sha256_file(input_file),
        "codebook_file": codebook_file, "codebook_sha256": sha256_file(codebook_file) if codebook_file else None,
        "python": platform.python_version(), "notes": notes,
    }
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--log", required=True); p.add_argument("--who", required=True)
    p.add_argument("--model", required=True); p.add_argument("--version", required=True)
    p.add_argument("--params", default="{}"); p.add_argument("--prompt", required=True)
    p.add_argument("--input", required=True); p.add_argument("--seed", default=None)
    p.add_argument("--codebook"); p.add_argument("--notes", default="")
    a = p.parse_args(argv)
    rec = log_run(a.log, a.who, a.model, a.version, json.loads(a.params), a.prompt, a.input, a.seed, a.codebook, a.notes)
    print(json.dumps(rec, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
