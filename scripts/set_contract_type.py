#!/usr/bin/env python3
"""
Usage:
  python scripts/set_contract_type.py list
  python scripts/set_contract_type.py set <project_index> <value>

Values: BTO | BOT | BTO/BOT | Others | (empty to clear)

Examples:
  python scripts/set_contract_type.py list
  python scripts/set_contract_type.py set 3 BTO/BOT
  python scripts/set_contract_type.py set 3 ""
"""

import json
import sys
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "data.json"
SCHEME = "รูปแบบการจัดสรรกรรมสิทธิ์"


def load():
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def save(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Saved.")


def get_ct(project):
    acs = project.get("additionalClassifications", [])
    ac = next((a for a in acs if a.get("scheme") == SCHEME), None)
    return ac.get("description", "") if ac else ""


def list_projects(projects):
    print(f"{'#':<4} {'Contract Type':<12} Project")
    print("-" * 80)
    for i, p in enumerate(projects):
        ct = get_ct(p) or "(empty)"
        title = p.get("title", p.get("name", "?"))[:60]
        print(f"{i:<4} {ct:<12} {title}")


def set_contract_type(projects, idx, value):
    p = projects[idx]
    acs = p.setdefault("additionalClassifications", [])
    existing = next((a for a in acs if a.get("scheme") == SCHEME), None)

    if not value:
        if existing:
            acs.remove(existing)
            print(f"Cleared contract type for project {idx}: {p.get('title', '')[:60]}")
        else:
            print("Already empty.")
        return

    if existing:
        existing["description"] = value
        existing["id"] = ""
    else:
        acs.append({"scheme": SCHEME, "id": "", "description": value})

    print(f"Set '{value}' on project {idx}: {p.get('title', '')[:60]}")


def main():
    args = sys.argv[1:]
    if not args or args[0] not in ("list", "set"):
        print(__doc__)
        sys.exit(1)

    data = load()
    projects = data if isinstance(data, list) else data.get("projects", [])

    if args[0] == "list":
        list_projects(projects)
        counts = {}
        for p in projects:
            ct = get_ct(p) or "(empty)"
            counts[ct] = counts.get(ct, 0) + 1
        print()
        print("Summary:")
        for k, v in sorted(counts.items()):
            print(f"  {k}: {v}")

    elif args[0] == "set":
        if len(args) < 3:
            print("Usage: set_contract_type.py set <index> <value>")
            sys.exit(1)
        idx = int(args[1])
        value = args[2]
        set_contract_type(projects, idx, value)
        save(data)


if __name__ == "__main__":
    main()
