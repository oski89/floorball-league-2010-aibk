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
TEAMS_CSV = DATA_DIR / "div3_orebro_vastmanland_teams.csv"
PLAYERS_CSV = DATA_DIR / "div3_orebro_vastmanland_players.csv"

TEAM_ASSET_FIELDS = [
    "team_logo",
    "field_asset",
    "rink_ads_asset",
    "side_ads_asset",
    "jersey_home",
    "jersey_away",
    "shorts_home",
    "shorts_away",
    "socks_home",
    "socks_away",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    teams = read_csv(TEAMS_CSV)
    players = read_csv(PLAYERS_CSV)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    missing_portraits: list[str] = []
    for player in players:
        portrait = player.get("portrait_file", "").strip()
        if portrait and not (PLAYERS_DIR / portrait).exists():
            missing_portraits.append(portrait)

    missing_team_assets: list[dict[str, str]] = []
    for team in teams:
        team_name = team.get("team_name", "")
        for field in TEAM_ASSET_FIELDS:
            asset_name = team.get(field, "").strip()
            if asset_name and not (TEAMS_DIR / asset_name).exists():
                missing_team_assets.append(
                    {"team_name": team_name, "field": field, "asset_name": asset_name}
                )

    payload = {
        "league": "Division 3 Örebro/Västmanland",
        "season": "2025/2026",
        "teams_count": len(teams),
        "players_count": len(players),
        "teams": teams,
        "priority_team": "Askersunds IBK H3",
        "priority_player": "Tobias Bäckström",
        "players": players,
        "validation": {
            "missing_portraits": missing_portraits,
            "missing_team_assets": missing_team_assets,
            "players_assets_present": sorted(p.name for p in PLAYERS_DIR.glob("*.png")),
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
    if missing_team_assets:
        print("Missing team assets:")
        for item in missing_team_assets:
            print(f" - {item['team_name']} {item['field']}: {item['asset_name']}")


if __name__ == "__main__":
    main()
