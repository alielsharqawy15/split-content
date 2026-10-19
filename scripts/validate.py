#!/usr/bin/env python3
"""Validates the content packs exactly like the app does (ContentPack.fromJson).

Run before pushing:  python3 scripts/validate.py
Also runs on every push via .github/workflows/validate.yml.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = 1
KINDS = {"words", "likely", "taboo", "ideas"}
ID = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
MAX_ITEMS = 500
MAX_TEXT = 160

errors: list[str] = []


def err(where: str, msg: str) -> None:
    errors.append(f"{where}: {msg}")


def text(v, where: str, what: str) -> str | None:
    if not isinstance(v, str) or not v.strip() or len(v.strip()) > MAX_TEXT:
        err(where, f"{what} must be non-empty text of at most {MAX_TEXT} characters")
        return None
    return v.strip()


def check_pack(path: Path, entry: dict) -> None:
    where = str(path.relative_to(ROOT))
    try:
        pack = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return err(where, "file listed in manifest.json does not exist")
    except json.JSONDecodeError as e:
        return err(where, f"invalid JSON: {e}")

    if pack.get("schema") != SCHEMA:
        err(where, f'"schema" must be {SCHEMA}')
    pid = pack.get("id")
    if not isinstance(pid, str) or not ID.match(pid):
        err(where, '"id" must be lowercase letters, digits and dashes')
    if pid != entry.get("id"):
        err(where, f'id "{pid}" does not match manifest id "{entry.get("id")}"')
    if not isinstance(pack.get("version"), int):
        err(where, '"version" must be an integer')
    elif pack["version"] != entry.get("version"):
        err(where, f'version {pack["version"]} does not match manifest version {entry.get("version")} — bump both')
    kind = pack.get("kind")
    if kind not in KINDS:
        err(where, f'"kind" must be one of {sorted(KINDS)}')
    name = pack.get("name")
    if not isinstance(name, dict):
        err(where, '"name" must be {"en": ..., "ar": ...}')
    else:
        text(name.get("en"), where, "name.en")
        text(name.get("ar"), where, "name.ar")

    items = pack.get("items")
    if not isinstance(items, list) or not items or len(items) > MAX_ITEMS:
        return err(where, f'"items" must be a list of 1–{MAX_ITEMS} entries')

    seen: set[str] = set()
    for i, item in enumerate(items):
        at = f"{where} item {i + 1}"
        if not isinstance(item, dict):
            err(at, "must be an object")
            continue
        if kind == "taboo":
            for lang in ("en", "ar"):
                side = item.get(lang)
                if not isinstance(side, dict):
                    err(at, f'"{lang}" must be {{"word": ..., "forbidden": [...]}}')
                    continue
                text(side.get("word"), at, f"{lang}.word")
                forbidden = side.get("forbidden")
                if not isinstance(forbidden, list) or not 3 <= len(forbidden) <= 5:
                    err(at, f"{lang}.forbidden must have 3–5 words")
                else:
                    for f in forbidden:
                        text(f, at, f"{lang}.forbidden word")
            key = str((item.get("en") or {}).get("word", "")).strip().lower()
        else:
            en = text(item.get("en"), at, "en")
            text(item.get("ar"), at, "ar")
            key = (en or "").lower()
        if key and key in seen:
            print(f"warning: {at}: duplicate “{key}” (the app keeps only the first)")
        seen.add(key)


def main() -> int:
    try:
        manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"manifest.json: {e}")
        return 1
    if manifest.get("schema") != SCHEMA:
        err("manifest.json", f'"schema" must be {SCHEMA}')
    ids: set[str] = set()
    for entry in manifest.get("packs", []):
        if entry.get("id") in ids:
            err("manifest.json", f'duplicate id "{entry.get("id")}"')
        ids.add(entry.get("id"))
        check_pack(ROOT / str(entry.get("file", "")), entry)

    listed = {str(ROOT / e.get("file", "")) for e in manifest.get("packs", [])}
    for f in (ROOT / "packs").glob("*.json"):
        if str(f) not in listed:
            print(f"warning: {f.relative_to(ROOT)} is not listed in manifest.json, so the app won't download it")

    if errors:
        print("\n".join(errors))
        print(f"\n{len(errors)} problem(s) found")
        return 1
    print(f"OK — {len(ids)} packs valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
