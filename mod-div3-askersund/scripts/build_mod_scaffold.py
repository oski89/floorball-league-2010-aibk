#!/usr/bin/env python3
"""Builds a Floorball League 2010 mod scaffold from CSV files.

This script intentionally avoids writing binary .teams/.players files directly.
It prepares deterministic resource manifests and validates that referenced assets exist.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PLAYERS_DIR = ROOT / "players"
TEAMS_DIR = ROOT / "teams"
OUT_DIR = ROOT / "build"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    teams = read_csv(DATA_DIR / "div3_orebro_vastmanland_teams.csv")
    askersund_players = read_csv(DATA_DIR / "askersund_h3_players.csv")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    missing_portraits: list[str] = []
    for player in askersund_players:
        portrait = player.get("portrait_file", "").strip()
        if portrait and not (PLAYERS_DIR / portrait).exists():
            missing_portraits.append(portrait)

    payload = {
        "league": "Division 3 Örebro/Västmanland",
        "season": "2024/2025",
        "teams_count": len(teams),
        "teams": teams,
        "priority_team": "Askersunds IBK H3",
        "players": askersund_players,
        "validation": {
            "missing_portraits": missing_portraits,
            "teams_assets_present": sorted(p.name for p in TEAMS_DIR.glob("*.png")),
        },
    }

    with (OUT_DIR / "mod_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Wrote {OUT_DIR / 'mod_manifest.json'}")
    if missing_portraits:
        print("Missing portraits:")
        for portrait in missing_portraits:
            print(f" - {portrait}")


if __name__ == "__main__":
    main()
